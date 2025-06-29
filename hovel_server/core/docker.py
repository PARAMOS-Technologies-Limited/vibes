import os
import shutil
import subprocess
import logging

logger = logging.getLogger(__name__)

def build_branch_image(branch_name):
    """Build Docker image for a branch"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            raise FileNotFoundError(f"Docker Compose file not found for branch {branch_name}")
        
        # Build the image using docker-compose
        result = subprocess.run([
            'docker-compose', '-f', 'docker-compose.yaml', 'build'
        ], capture_output=True, text=True, cwd=branch_dir, check=True)
        
        logger.info(f"Built Docker image for branch {branch_name}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build Docker image for branch {branch_name}: {e}")
        logger.error(f"stdout: {e.stdout}")
        logger.error(f"stderr: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Error building Docker image for branch {branch_name}: {e}")
        return False

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
        
        # Step 4: Delete branch directory and all files (including .branch file)
        if os.path.exists(branch_dir):
            shutil.rmtree(branch_dir)
            logger.info(f"Deleted branch directory: {branch_dir}")
        
        # Step 5: Branch tracking is automatically removed when directory is deleted
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