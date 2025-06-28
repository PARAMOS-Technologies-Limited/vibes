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

def duplicate_app_directory(branch_name):
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
        create_branch_env_file(branch_name, target_dir)
        
        # Create branch-specific Docker Compose file
        create_branch_docker_compose(branch_name, target_dir)
        
        return target_dir
    except Exception as e:
        logger.error(f"Error duplicating app directory: {e}")
        raise

def create_branch_env_file(branch_name, target_dir):
    """Create environment file for the branch"""
    try:
        env_content = f"""# Environment variables for branch: {branch_name}
FLASK_APP=app.py
FLASK_ENV=development
PORT=8000
BRANCH_NAME={branch_name}
"""
        
        env_file = os.path.join(target_dir, '.env')
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created environment file: {env_file}")
    except Exception as e:
        logger.warning(f"Could not create environment file: {e}")

def create_branch_docker_compose(branch_name, target_dir):
    """Create Docker Compose file for the branch"""
    try:
        # Get the port for this branch
        port = BRANCH_PORTS.get(branch_name, get_next_available_port())
        
        compose_content = f"""services:
  app-{branch_name}:
    build: .
    ports:
      - "{port}:8000"
    volumes:
      - .:/app
    env_file:
      - .env
    environment:
      - FLASK_APP=app.py
      - FLASK_ENV=development
      - PORT=8000
      - BRANCH_NAME={branch_name}
    restart: unless-stopped
    container_name: hovel-app-{branch_name}
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
    
    # Generate Docker Compose file
    generate_docker_compose_for_branch(branch_name, port)
    
    return config

def generate_docker_compose_for_branch(branch_name, port):
    """Generate Docker Compose file for a specific branch"""
    try:
        # Read template
        template_file = 'docker-compose.branch.template.yaml'
        if os.path.exists(template_file):
            with open(template_file, 'r') as f:
                template_content = f.read()
            
            # Replace placeholders
            compose_content = template_content.replace('{{BRANCH_NAME}}', branch_name)
            compose_content = compose_content.replace('{{PORT}}', str(port))
            
            # Write generated compose file
            compose_file = f'branches/{branch_name}/docker-compose.yaml'
            with open(compose_file, 'w') as f:
                f.write(compose_content)
            
            logger.info(f"Generated Docker Compose file: {compose_file}")
    except Exception as e:
        logger.warning(f"Could not generate Docker Compose file: {e}")

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
            '/api/branch'
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
        app_dir = duplicate_app_directory(branch_name)
        
        # Create branch configuration
        config = create_branch_config(branch_name, port, app_dir)
        
        logger.info(f"Created branch {branch_name} on port {port}")
        
        return jsonify({
            'message': f'Branch {branch_name} created successfully',
            'branch_name': branch_name,
            'port': port,
            'app_directory': app_dir,
            'git_branch': branch_name,
            'status': 'created',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 201
        
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