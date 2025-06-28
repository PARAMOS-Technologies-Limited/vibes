#!/usr/bin/env python3
"""
Main API Server
This is the primary server file that handles the API endpoints and business logic.
"""

import os
import sys
import logging
import shutil
import subprocess
import json
from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configuration
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

# Track branch ports (in a real app, this would be in a database)
BRANCH_PORTS = {}
BASE_PORT = 8000

def get_next_available_port():
    """Get the next available port starting from BASE_PORT"""
    used_ports = set(BRANCH_PORTS.values())
    port = BASE_PORT + 1
    while port in used_ports:
        port += 1
    return port

def create_git_branch(branch_name):
    """Create a new git branch"""
    try:
        # Check if we're in a git repository
        result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd='.')
        if result.returncode != 0:
            logger.warning("Not in a git repository or git not available - skipping git branch creation")
            return True
        
        # Create and checkout new branch
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, cwd='.')
        logger.info(f"Created and checked out branch: {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Git command failed: {e}")
        logger.warning("Continuing without git branch creation")
        return True
    except FileNotFoundError:
        logger.warning("Git command not found - skipping git branch creation")
        return True
    except Exception as e:
        logger.error(f"Error creating git branch: {e}")
        logger.warning("Continuing without git branch creation")
        return True

def duplicate_app_directory(branch_name, port):
    """Duplicate the app directory for the new branch"""
    try:
        source_dir = 'app'
        target_dir = f'branches/{branch_name}'
        
        # Remove existing directory if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Copy the app directory
        shutil.copytree(source_dir, target_dir)
        logger.info(f"Duplicated app directory to {target_dir}")
        
        # Create branch-specific environment file
        create_branch_env_file(branch_name, target_dir, port)
        
        # Create branch-specific Docker Compose file
        create_branch_docker_compose(branch_name, target_dir, port)
        
        return target_dir
    except Exception as e:
        logger.error(f"Error duplicating app directory: {e}")
        raise

def create_branch_env_file(branch_name, target_dir, port):
    """Create environment file for the branch"""
    try:
        env_content = f"""# Environment variables for branch: {branch_name}
FLASK_APP=app.py
FLASK_ENV=development
PORT={port}
BRANCH_NAME={branch_name}
"""
        
        env_file = os.path.join(target_dir, '.env')
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created environment file: {env_file}")
    except Exception as e:
        logger.warning(f"Could not create environment file: {e}")

def create_branch_docker_compose(branch_name, target_dir, port):
    """Create Docker Compose file for the branch"""
    try:
        compose_content = f"""services:
  app-{branch_name}:
    build: .
    ports:
      - "{port}:8000"
    env_file:
      - .env
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=development
      - PORT={port}
      - BRANCH_NAME={branch_name}
    restart: unless-stopped
    container_name: hovel-app-{branch_name}
    networks:
      - hovel-shared

networks:
  hovel-shared:
    external: true
"""
        
        compose_file = os.path.join(target_dir, 'docker-compose.yaml')
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        logger.info(f"Created Docker Compose file: {compose_file}")
    except Exception as e:
        logger.warning(f"Could not create Docker Compose file: {e}")

def create_branch_config(branch_name, port, app_dir):
    """Create configuration for the new branch"""
    config = {
        'branch_name': branch_name,
        'port': port,
        'app_directory': app_dir,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'status': 'created'
    }
    
    # Save config to file
    config_file = f'branches/{branch_name}/branch_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Note: Docker Compose file is already created by create_branch_docker_compose function
    
    return config

def start_branch_container(branch_name):
    """Start Docker container for a branch"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            raise FileNotFoundError(f"Docker Compose file not found for branch {branch_name}")
        
        # Start the container using docker-compose
        # Use just the filename since cwd is set to branch_dir
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yaml', 'up', '-d'
        ], capture_output=True, text=True, cwd=branch_dir, check=True)
        
        logger.info(f"Started Docker container for branch {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start Docker container for branch {branch_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error starting Docker container for branch {branch_name}: {e}")
        return False

def stop_branch_container(branch_name):
    """Stop Docker container for a branch"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            raise FileNotFoundError(f"Docker Compose file not found for branch {branch_name}")
        
        # Stop the container using docker-compose
        # Use just the filename since cwd is set to branch_dir
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yaml', 'down'
        ], capture_output=True, text=True, cwd=branch_dir, check=True)
        
        logger.info(f"Stopped Docker container for branch {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop Docker container for branch {branch_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error stopping Docker container for branch {branch_name}: {e}")
        return False

def get_branch_container_status(branch_name):
    """Get the status of a branch's Docker container"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            return {'status': 'not_found', 'message': 'Docker Compose file not found'}
        
        # Check container status using docker-compose
        # Use just the filename since cwd is set to branch_dir
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yaml', 'ps'
        ], capture_output=True, text=True, cwd=branch_dir, check=True)
        
        if 'Up' in result.stdout:
            return {'status': 'running', 'details': result.stdout.strip()}
        elif 'Exit' in result.stdout:
            return {'status': 'stopped', 'details': result.stdout.strip()}
        else:
            return {'status': 'unknown', 'details': result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {'status': 'error', 'message': f'Failed to check status: {e.stderr}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def get_branch_logs(branch_name, lines=50):
    """Get logs from a branch's Docker container"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            return {'error': 'Docker Compose file not found'}
        
        # Get logs using docker-compose
        # Use just the filename since cwd is set to branch_dir
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yaml', 'logs', '--tail', str(lines)
        ], capture_output=True, text=True, cwd=branch_dir, check=True)
        
        return {'logs': result.stdout.strip()}
    except subprocess.CalledProcessError as e:
        return {'error': f'Failed to get logs: {e.stderr}'}
    except Exception as e:
        return {'error': str(e)}

def cleanup_branch_environment(branch_name):
    """Completely cleanup a branch environment - stop container, remove it, and delete files"""
    try:
        branch_dir = f'branches/{branch_name}'
        
        # Step 1: Stop and remove Docker container
        if os.path.exists(os.path.join(branch_dir, 'docker-compose.yaml')):
            try:
                # Stop the container
                subprocess.run([
                    'docker-compose', '-f', 'docker-compose.yaml', 'down', '--rmi', 'all', '--volumes'
                ], capture_output=True, text=True, cwd=branch_dir, check=True)
                logger.info(f"Stopped and removed Docker container for branch {branch_name}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to stop Docker container for branch {branch_name}: {e}")
            except Exception as e:
                logger.warning(f"Error stopping Docker container for branch {branch_name}: {e}")
        
        # Step 2: Remove any remaining containers with the branch name
        try:
            subprocess.run([
                'docker', 'rm', '-f', f'hovel-app-{branch_name}'
            ], capture_output=True, text=True, check=False)  # Don't fail if container doesn't exist
        except Exception as e:
            logger.warning(f"Error removing container for branch {branch_name}: {e}")
        
        # Step 3: Remove any images with the branch name
        try:
            subprocess.run([
                'docker', 'rmi', '-f', f'{branch_name}-app-{branch_name}'
            ], capture_output=True, text=True, check=False)  # Don't fail if image doesn't exist
        except Exception as e:
            logger.warning(f"Error removing image for branch {branch_name}: {e}")
        
        # Step 4: Delete branch directory and all files
        if os.path.exists(branch_dir):
            shutil.rmtree(branch_dir)
            logger.info(f"Deleted branch directory: {branch_dir}")
        
        # Step 5: Remove from tracking
        if branch_name in BRANCH_PORTS:
            del BRANCH_PORTS[branch_name]
            logger.info(f"Removed branch {branch_name} from tracking")
        
        # Step 6: Try to delete git branch (optional)
        try:
            subprocess.run(['git', 'branch', '-D', branch_name], capture_output=True, text=True, check=False)
            logger.info(f"Deleted git branch: {branch_name}")
        except Exception as e:
            logger.warning(f"Could not delete git branch {branch_name}: {e}")
        
        return True
    except Exception as e:
        logger.error(f"Error cleaning up branch {branch_name}: {e}")
        return False

@app.before_request
def log_request():
    """Log all incoming requests"""
    logger.info(f"{request.method} {request.path} - {request.remote_addr}")

@app.after_request
def log_response(response):
    """Log all outgoing responses"""
    logger.info(f"Response: {response.status_code}")
    return response

@app.route('/')
def root():
    """Root endpoint with server information"""
    return jsonify({
        'message': 'Welcome to the Main API Server!',
        'server': 'server.py',
        'status': 'running',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'version': '1.0.0'
    })

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'main-api-server',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'uptime': 'running'
    })

@app.route('/api/status')
def api_status():
    """API status endpoint"""
    return jsonify({
        'api_status': 'operational',
        'endpoints': [
            '/',
            '/health',
            '/api/status',
            '/api/data',
            '/api/process',
            '/api/branch',
            '/api/branches',
            '/api/branch/{branch_name}/start',
            '/api/branch/{branch_name}/stop',
            '/api/branch/{branch_name}/status',
            '/api/branch/{branch_name}/logs',
            '/api/branch/{branch_name}/restart',
            '/api/branch/{branch_name} (DELETE)'
        ],
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/branch', methods=['POST'])
def create_branch():
    """Create a new branch with duplicated app directory"""
    try:
        data = request.get_json()
        if not data or 'branch_name' not in data:
            return jsonify({'error': 'branch_name is required in request body'}), 400
        
        branch_name = data['branch_name']
        auto_start = data.get('auto_start', False)  # New parameter to auto-start container
        
        # Validate branch name
        if not branch_name or not branch_name.strip():
            return jsonify({'error': 'branch_name cannot be empty'}), 400
        
        # Check if branch already exists
        if branch_name in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} already exists'}), 409
        
        # Get next available port and store it first
        port = get_next_available_port()
        BRANCH_PORTS[branch_name] = port
        
        # Create git branch
        create_git_branch(branch_name)
        
        # Duplicate app directory (this will create env files and docker compose)
        app_dir = duplicate_app_directory(branch_name, port)
        
        # Create branch configuration
        config = create_branch_config(branch_name, port, app_dir)
        
        # Auto-start container if requested
        container_started = False
        if auto_start:
            container_started = start_branch_container(branch_name)
            if container_started:
                logger.info(f"Auto-started Docker container for branch {branch_name}")
            else:
                logger.warning(f"Failed to auto-start Docker container for branch {branch_name}")
        
        logger.info(f"Created branch {branch_name} on port {port}")
        
        response_data = {
            'message': f'Branch {branch_name} created successfully',
            'branch_name': branch_name,
            'port': port,
            'app_directory': app_dir,
            'git_branch': branch_name,
            'status': 'created',
            'auto_start': auto_start,
            'container_started': container_started,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error creating branch: {str(e)}")
        return jsonify({'error': f'Failed to create branch: {str(e)}'}), 500

@app.route('/api/branches', methods=['GET'])
def list_branches():
    """List all created branches"""
    try:
        branches = []
        for branch_name, port in BRANCH_PORTS.items():
            config_file = f'branches/{branch_name}/branch_config.json'
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    branches.append(config)
        
        return jsonify({
            'branches': branches,
            'count': len(branches),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing branches: {str(e)}")
        return jsonify({'error': f'Failed to list branches: {str(e)}'}), 500

@app.route('/api/data', methods=['GET'])
def get_data():
    """Get sample data"""
    return jsonify({
        'data': [
            {'id': 1, 'name': 'Item 1', 'value': 100},
            {'id': 2, 'name': 'Item 2', 'value': 200},
            {'id': 3, 'name': 'Item 3', 'value': 300}
        ],
        'count': 3,
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })

@app.route('/api/process', methods=['POST'])
def process_data():
    """Process incoming data"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Process the data (example processing)
        processed_data = {
            'received': data,
            'processed_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'success'
        }
        
        logger.info(f"Processed data: {data}")
        return jsonify(processed_data), 200
        
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/branch/<branch_name>/start', methods=['POST'])
def start_branch(branch_name):
    """Start Docker container for a branch"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = start_branch_container(branch_name)
        if success:
            return jsonify({
                'message': f'Branch {branch_name} started successfully',
                'branch_name': branch_name,
                'status': 'started',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({'error': f'Failed to start branch {branch_name}'}), 500
            
    except Exception as e:
        logger.error(f"Error starting branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to start branch: {str(e)}'}), 500

@app.route('/api/branch/<branch_name>/stop', methods=['POST'])
def stop_branch(branch_name):
    """Stop Docker container for a branch"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = stop_branch_container(branch_name)
        if success:
            return jsonify({
                'message': f'Branch {branch_name} stopped successfully',
                'branch_name': branch_name,
                'status': 'stopped',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({'error': f'Failed to stop branch {branch_name}'}), 500
            
    except Exception as e:
        logger.error(f"Error stopping branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to stop branch: {str(e)}'}), 500

@app.route('/api/branch/<branch_name>/status', methods=['GET'])
def get_branch_status(branch_name):
    """Get the status of a branch's Docker container"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        status = get_branch_container_status(branch_name)
        return jsonify({
            'branch_name': branch_name,
            'container_status': status,
            'port': BRANCH_PORTS.get(branch_name),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting status for branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to get branch status: {str(e)}'}), 500

@app.route('/api/branch/<branch_name>/logs', methods=['GET'])
def get_branch_logs_endpoint(branch_name):
    """Get logs from a branch's Docker container"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        lines = request.args.get('lines', 50, type=int)
        logs = get_branch_logs(branch_name, lines)
        
        if 'error' in logs:
            return jsonify(logs), 500
        
        return jsonify({
            'branch_name': branch_name,
            'logs': logs['logs'],
            'lines': lines,
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting logs for branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to get branch logs: {str(e)}'}), 500

@app.route('/api/branch/<branch_name>/restart', methods=['POST'])
def restart_branch(branch_name):
    """Restart Docker container for a branch"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        # Stop the container first
        stop_success = stop_branch_container(branch_name)
        if not stop_success:
            logger.warning(f"Failed to stop branch {branch_name} before restart")
        
        # Start the container
        start_success = start_branch_container(branch_name)
        if start_success:
            return jsonify({
                'message': f'Branch {branch_name} restarted successfully',
                'branch_name': branch_name,
                'status': 'restarted',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({'error': f'Failed to restart branch {branch_name}'}), 500
            
    except Exception as e:
        logger.error(f"Error restarting branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to restart branch: {str(e)}'}), 500

@app.route('/api/branch/<branch_name>', methods=['DELETE'])
def delete_branch(branch_name):
    """Completely cleanup and delete a branch environment"""
    try:
        if branch_name not in BRANCH_PORTS:
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = cleanup_branch_environment(branch_name)
        if success:
            return jsonify({
                'message': f'Branch {branch_name} completely cleaned up and deleted',
                'branch_name': branch_name,
                'status': 'deleted',
                'actions_performed': [
                    'stopped_docker_container',
                    'removed_docker_container',
                    'removed_docker_image',
                    'deleted_branch_files',
                    'removed_from_tracking',
                    'deleted_git_branch'
                ],
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({'error': f'Failed to cleanup branch {branch_name}'}), 500
            
    except Exception as e:
        logger.error(f"Error deleting branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to delete branch: {str(e)}'}), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'error': 'Internal server error',
        'message': 'Something went wrong on the server',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 500

def main():
    """Main function to run the server"""
    port = int(os.environ.get('PORT', 8000))
    host = os.environ.get('HOST', '0.0.0.0')
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Starting server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    
    try:
        app.run(host=host, port=port, debug=debug)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 