from flask import Blueprint, jsonify, request
import logging
from datetime import datetime
from ..core import utils, git, gemini, docker, branch

logger = logging.getLogger(__name__)

branch_bp = Blueprint('branch', __name__)

@branch_bp.route('/api/branch', methods=['POST'])
def create_branch():
    """Create a new branch with duplicated app directory"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Request body is required'}), 400
        
        # Check for required fields
        if 'branch_name' not in data:
            return jsonify({'error': 'branch_name is required in request body'}), 400
        
        if 'gemini_api_key' not in data:
            return jsonify({
                'error': 'gemini_api_key is required',
                'message': 'Please provide a valid Gemini API key in the request body'
            }), 401
        
        # Extract and validate the API key
        api_key = data['gemini_api_key']
        is_valid, message = gemini.validate_gemini_api_key(api_key)
        if not is_valid:
            return jsonify({
                'error': 'Invalid Gemini API key',
                'message': message
            }), 401
        
        branch_name = data['branch_name']
        auto_start = data.get('auto_start', False)  # New parameter to auto-start container
        
        # Validate branch name
        if not branch_name or not branch_name.strip():
            return jsonify({'error': 'branch_name cannot be empty'}), 400
        
        # Check if branch already exists
        if utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} already exists'}), 409
        
        # Get next available port
        port = utils.get_next_available_port()
        
        # Create git branch
        git.create_git_branch(branch_name)
        
        # Duplicate app directory (this will create env files and docker compose)
        app_dir = branch.duplicate_app_directory(branch_name, port, api_key)
        
        # Create branch configuration
        config = branch.create_branch_config(branch_name, port, app_dir)
        
        # Save complete branch information to .branch file
        branch_info = {
            'branch_name': branch_name,
            'port': port,
            'app_directory': app_dir,
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'status': 'created',
            'git_branch': branch_name,
            'gemini_api_validated': True,
            'gemini_config_created': True,
            'gemini_config_path': f'{app_dir}/.gemini/config.json'
        }
        utils.save_branch_info(branch_name, branch_info)
        
        # Auto-start container if requested
        container_started = False
        if auto_start:
            container_started = docker.start_branch_container(branch_name)
            if container_started:
                logger.info(f"Auto-started Docker container for branch {branch_name}")
                # Update branch info with container status
                branch_info['container_started'] = True
                branch_info['status'] = 'running'
                utils.save_branch_info(branch_name, branch_info)
            else:
                logger.warning(f"Failed to auto-start Docker container for branch {branch_name}")
                branch_info['container_started'] = False
                utils.save_branch_info(branch_name, branch_info)
        
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
            'gemini_api_validated': True,
            'gemini_config_created': True,
            'gemini_config_path': f'{app_dir}/.gemini/config.json',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        logger.error(f"Error creating branch: {str(e)}")
        return jsonify({'error': f'Failed to create branch: {str(e)}'}), 500

@branch_bp.route('/api/branches', methods=['GET'])
def list_branches():
    """List all created branches"""
    try:
        branches = []
        all_branches = utils.get_all_branches()
        
        for branch_name, branch_info in all_branches.items():
            branches.append(branch_info)
        
        return jsonify({
            'branches': branches,
            'count': len(branches),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Error listing branches: {str(e)}")
        return jsonify({'error': f'Failed to list branches: {str(e)}'}), 500

@branch_bp.route('/api/branch/<branch_name>/start', methods=['POST'])
def start_branch(branch_name):
    """Start Docker container for a branch"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = docker.start_branch_container(branch_name)
        if success:
            # Update branch status in .branch file
            branch_info = utils.get_branch_info(branch_name)
            if branch_info:
                branch_info['status'] = 'running'
                branch_info['container_started'] = True
                utils.save_branch_info(branch_name, branch_info)
            
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

@branch_bp.route('/api/branch/<branch_name>/stop', methods=['POST'])
def stop_branch(branch_name):
    """Stop Docker container for a branch"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = docker.stop_branch_container(branch_name)
        if success:
            # Update branch status in .branch file
            branch_info = utils.get_branch_info(branch_name)
            if branch_info:
                branch_info['status'] = 'stopped'
                branch_info['container_started'] = False
                utils.save_branch_info(branch_name, branch_info)
            
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

@branch_bp.route('/api/branch/<branch_name>/status', methods=['GET'])
def get_branch_status(branch_name):
    """Get the status of a branch's Docker container"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        branch_info = utils.get_branch_info(branch_name)
        if not branch_info:
            return jsonify({'error': f'Branch {branch_name} info not found'}), 404
        
        status = docker.get_branch_container_status(branch_name)
        return jsonify({
            'branch_name': branch_name,
            'container_status': status,
            'port': branch_info.get('port'),
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting status for branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to get branch status: {str(e)}'}), 500

@branch_bp.route('/api/branch/<branch_name>/logs', methods=['GET'])
def get_branch_logs_endpoint(branch_name):
    """Get logs from a branch's Docker container"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        lines = request.args.get('lines', 50, type=int)
        logs = docker.get_branch_logs(branch_name, lines)
        
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

@branch_bp.route('/api/branch/<branch_name>/restart', methods=['POST'])
def restart_branch(branch_name):
    """Restart Docker container for a branch"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        # Stop the container first
        stop_success = docker.stop_branch_container(branch_name)
        if not stop_success:
            logger.warning(f"Failed to stop branch {branch_name} before restart")
        
        # Start the container
        start_success = docker.start_branch_container(branch_name)
        if start_success:
            # Update branch status in .branch file
            branch_info = utils.get_branch_info(branch_name)
            if branch_info:
                branch_info['status'] = 'running'
                branch_info['container_started'] = True
                utils.save_branch_info(branch_name, branch_info)
            
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

@branch_bp.route('/api/branch/<branch_name>', methods=['DELETE'])
def delete_branch(branch_name):
    """Completely cleanup and delete a branch environment"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        success = docker.cleanup_branch_environment(branch_name)
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