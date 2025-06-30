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

def start_branch_container(branch_name, services=None):
    """Start Docker container for a branch"""
    try:
        branch_dir = f'branches/{branch_name}'
        compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
        
        if not os.path.exists(compose_file):
            raise FileNotFoundError(f"Docker Compose file not found for branch {branch_name}")
        
        # Build command based on whether specific services are requested
        if services and isinstance(services, list):
            # Start specific services
            cmd = ['docker-compose', '-f', 'docker-compose.yaml', 'up', '-d'] + services
            logger.info(f"Starting specific services for branch {branch_name}: {services}")
        else:
            # Start all services
            cmd = ['docker-compose', '-f', 'docker-compose.yaml', 'up', '-d']
            logger.info(f"Starting all services for branch {branch_name}")
        
        # Start the container using docker-compose
        # Use just the filename since cwd is set to branch_dir
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=branch_dir, check=True)
        
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
        
        # Parse the docker-compose ps output
        if 'Up' in result.stdout:
            # Parse container details from the output
            container_info = parse_container_details(result.stdout.strip())
            return {
                'status': 'running', 
                'details': container_info
            }
        elif 'Exit' in result.stdout:
            container_info = parse_container_details(result.stdout.strip())
            return {
                'status': 'stopped', 
                'details': container_info
            }
        else:
            return {
                'status': 'unknown', 
                'details': result.stdout.strip()
            }
    except subprocess.CalledProcessError as e:
        return {'status': 'error', 'message': f'Failed to check status: {e.stderr}'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

def parse_container_details(ps_output):
    """Parse docker-compose ps output into structured JSON"""
    try:
        lines = ps_output.strip().split('\n')
        if len(lines) < 2:  # Need header + at least one container
            return {'raw_output': ps_output}
        
        # Parse header to get column positions
        header = lines[0]
        containers = []
        
        # Find column positions based on header
        name_pos = header.find('NAME')
        image_pos = header.find('IMAGE')
        command_pos = header.find('COMMAND')
        service_pos = header.find('SERVICE')
        created_pos = header.find('CREATED')
        status_pos = header.find('STATUS')
        ports_pos = header.find('PORTS')
        
        # Parse each container line
        for line in lines[1:]:
            if line.strip():
                container = {}
                
                # Extract fields based on column positions
                if name_pos >= 0 and name_pos < len(line):
                    container['name'] = line[name_pos:image_pos].strip() if image_pos > name_pos else line[name_pos:].strip()
                
                if image_pos >= 0 and image_pos < len(line):
                    container['image'] = line[image_pos:command_pos].strip() if command_pos > image_pos else line[image_pos:].strip()
                
                if command_pos >= 0 and command_pos < len(line):
                    container['command'] = line[command_pos:service_pos].strip() if service_pos > command_pos else line[command_pos:].strip()
                
                if service_pos >= 0 and service_pos < len(line):
                    container['service'] = line[service_pos:created_pos].strip() if created_pos > service_pos else line[service_pos:].strip()
                
                if created_pos >= 0 and created_pos < len(line):
                    container['created'] = line[created_pos:status_pos].strip() if status_pos > created_pos else line[created_pos:].strip()
                
                if status_pos >= 0 and status_pos < len(line):
                    container['status'] = line[status_pos:ports_pos].strip() if ports_pos > status_pos else line[status_pos:].strip()
                
                if ports_pos >= 0 and ports_pos < len(line):
                    container['ports'] = line[ports_pos:].strip()
                
                containers.append(container)
        
        if len(containers) == 1:
            return containers[0]  # Return single container as object
        else:
            return {'containers': containers}  # Return multiple containers as array
            
    except Exception as e:
        logger.error(f"Error parsing container details: {e}")
        return {'raw_output': ps_output, 'parse_error': str(e)}

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

def execute_in_branch_container(branch_name, command, detach=False):
    """Execute a command inside a branch's Docker container"""
    try:
        # Get the container name for this branch
        container_name = f'hovel-app-{branch_name}'
        
        # Check if container is running
        status = get_branch_container_status(branch_name)
        if status.get('status') != 'running':
            raise Exception(f"Container for branch {branch_name} is not running")
        
        # Execute command in container
        cmd = ['docker', 'exec']
        if detach:
            cmd.append('-d')
        cmd.extend([container_name] + command)
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        logger.info(f"Executed command in container {container_name}: {' '.join(command)}")
        return {
            'success': True,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'return_code': result.returncode
        }
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to execute command in container for branch {branch_name}: {e}")
        return {
            'success': False,
            'stdout': e.stdout,
            'stderr': e.stderr,
            'return_code': e.returncode,
            'error': str(e)
        }
    except Exception as e:
        logger.error(f"Error executing command in container for branch {branch_name}: {e}")
        return {
            'success': False,
            'error': str(e)
        }

def start_ttyd_session(branch_name, port=7681):
    """Start a ttyd session with gemini-cli in a branch container"""
    try:
        # Check if container is running
        status = get_branch_container_status(branch_name)
        if status.get('status') != 'running':
            raise Exception(f"Container for branch {branch_name} is not running")
        
        # Start ttyd with gemini-cli in detached mode
        command = ['ttyd', '-o', '-W', '-p', str(port), 'gemini']
        result = execute_in_branch_container(branch_name, command, detach=True)
        
        if result['success']:
            logger.info(f"Started ttyd session for branch {branch_name} on port {port}")
            return {
                'success': True,
                'port': port,
                'url': f"http://localhost:{port}",
                'message': f"ttyd session started on port {port}"
            }
        else:
            raise Exception(f"Failed to start ttyd session: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        logger.error(f"Error starting ttyd session for branch {branch_name}: {e}")
        return {
            'success': False,
            'error': str(e)
        } 