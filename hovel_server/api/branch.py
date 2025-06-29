from flask import Blueprint, jsonify, request
import logging
from datetime import datetime
from ..core import utils, git, gemini, docker, branch, background_tasks

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
        auto_start = data.get('auto_start', True)  # Default to True for immediate build
        
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
            'gemini_settings_created': True,
            'gemini_settings_path': f'{app_dir}/.gemini/settings.json'
        }
        utils.save_branch_info(branch_name, branch_info)
        
        # Start background build task if auto_start is enabled
        task_id = None
        if auto_start:
            task_id = background_tasks.start_branch_build_task(branch_name)
            branch_info['build_task_id'] = task_id
            branch_info['status'] = 'building'
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
            'build_task_id': task_id,
            'gemini_api_validated': True,
            'gemini_settings_created': True,
            'gemini_settings_path': f'{app_dir}/.gemini/settings.json',
            'timestamp': datetime.utcnow().isoformat() + 'Z'
        }
        
        # Return 202 Accepted if auto_start is enabled, otherwise 201 Created
        status_code = 202 if auto_start else 201
        return jsonify(response_data), status_code
        
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

@branch_bp.route('/api/branch/<branch_name>/build-status', methods=['GET'])
def get_branch_build_status(branch_name):
    """Get the build status for a branch"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        # Get build status from background tasks
        build_status = background_tasks.get_branch_build_status(branch_name)
        
        if build_status is None:
            return jsonify({'error': f'No build status found for branch {branch_name}'}), 404
        
        # If it's a BackgroundTask object, convert to dict
        if hasattr(build_status, 'task_id'):
            response_data = {
                'branch_name': branch_name,
                'task_id': getattr(build_status, 'task_id', None),
                'status': getattr(build_status, 'status', 'unknown'),
                'progress': getattr(build_status, 'progress', 0),
                'message': getattr(build_status, 'message', ''),
                'created_at': getattr(build_status, 'created_at', None),
                'started_at': getattr(build_status, 'started_at', None),
                'completed_at': getattr(build_status, 'completed_at', None),
                'error': getattr(build_status, 'error', None),
                'result': getattr(build_status, 'result', None),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        else:
            # It's a dict from branch_info
            response_data = {
                'branch_name': branch_name,
                'status': build_status.get('status', 'unknown'),
                'message': build_status.get('message', 'No build task found'),
                'branch_info': build_status.get('branch_info'),
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }
        
        return jsonify(response_data), 200
        
    except Exception as e:
        logger.error(f"Error getting build status for branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to get build status: {str(e)}'}), 500

@branch_bp.route('/api/branch/<branch_name>/gemini-session', methods=['POST'])
def start_gemini_session(branch_name):
    """Start a ttyd session with gemini-cli in a branch container"""
    try:
        if not utils.branch_exists(branch_name):
            return jsonify({'error': f'Branch {branch_name} not found'}), 404
        
        # Get branch info to check if container is running
        branch_info = utils.get_branch_info(branch_name)
        if not branch_info:
            return jsonify({'error': f'Branch {branch_name} info not found'}), 404
        
        # Check if container is running
        container_status = docker.get_branch_container_status(branch_name)
        if container_status.get('status') != 'running':
            return jsonify({
                'error': f'Branch {branch_name} container is not running',
                'container_status': container_status.get('status'),
                'message': 'Please start the branch container first using /api/branch/{branch_name}/start'
            }), 400
        
        # Get the port for this branch to calculate ttyd port
        branch_port = branch_info.get('port', 8000)
        # Use a port offset for ttyd (branch_port + 1000)
        ttyd_port = branch_port + 1000
        
        # Start ttyd session
        result = docker.start_ttyd_session(branch_name, ttyd_port)
        
        if result['success']:
            # Update branch info with ttyd session details
            branch_info['ttyd_session'] = {
                'port': ttyd_port,
                'url': result['url'],
                'started_at': datetime.utcnow().isoformat() + 'Z',
                'command': 'ttyd -o -W gemini'
            }
            utils.save_branch_info(branch_name, branch_info)
            
            return jsonify({
                'message': f'Gemini session started successfully for branch {branch_name}',
                'branch_name': branch_name,
                'ttyd_port': ttyd_port,
                'ttyd_url': result['url'],
                'gemini_command': 'ttyd -o -W gemini',
                'access_url': f"http://localhost:{ttyd_port}",
                'instructions': 'Open the access_url in your browser to access the Gemini CLI terminal',
                'timestamp': datetime.utcnow().isoformat() + 'Z'
            }), 200
        else:
            return jsonify({
                'error': f'Failed to start Gemini session for branch {branch_name}',
                'details': result.get('error', 'Unknown error')
            }), 500
            
    except Exception as e:
        logger.error(f"Error starting Gemini session for branch {branch_name}: {str(e)}")
        return jsonify({'error': f'Failed to start Gemini session: {str(e)}'}), 500 