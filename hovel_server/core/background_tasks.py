import threading
import time
import logging
from datetime import datetime
from . import docker, utils

logger = logging.getLogger(__name__)

# Global dictionary to track background tasks
background_tasks = {}

class BackgroundTask:
    """Represents a background task with status tracking"""
    
    def __init__(self, task_id, task_type, branch_name):
        self.task_id = task_id
        self.task_type = task_type
        self.branch_name = branch_name
        self.status = 'pending'
        self.progress = 0
        self.message = 'Task queued'
        self.created_at = datetime.utcnow().isoformat() + 'Z'
        self.started_at = None
        self.completed_at = None
        self.error = None
        self.result = None

def start_branch_build_task(branch_name):
    """Start a background task to build and start a Docker container for a branch"""
    task_id = f"build_{branch_name}_{int(time.time())}"
    
    # Create task object
    task = BackgroundTask(task_id, 'branch_build', branch_name)
    background_tasks[task_id] = task
    
    # Start background thread
    thread = threading.Thread(
        target=_build_branch_container,
        args=(task_id, branch_name),
        daemon=True
    )
    thread.start()
    
    return task_id

def _build_branch_container(task_id, branch_name):
    """Background function to build and start Docker container"""
    task = background_tasks[task_id]
    
    try:
        # Update task status
        task.status = 'building'
        task.started_at = datetime.utcnow().isoformat() + 'Z'
        task.message = 'Building Docker container...'
        task.progress = 10
        
        # Update branch status
        branch_info = utils.get_branch_info(branch_name)
        if branch_info:
            branch_info['status'] = 'building'
            branch_info['build_task_id'] = task_id
            utils.save_branch_info(branch_name, branch_info)
        
        # Step 1: Build the Docker image
        task.message = 'Building Docker image...'
        task.progress = 20
        
        build_success = docker.build_branch_image(branch_name)
        if not build_success:
            raise Exception("Failed to build Docker image")
        
        task.progress = 50
        task.message = 'Docker image built successfully'
        
        # Step 2: Start the container
        task.message = 'Starting Docker container...'
        task.progress = 70
        
        start_success = docker.start_branch_container(branch_name)
        if not start_success:
            raise Exception("Failed to start Docker container")
        
        task.progress = 90
        task.message = 'Docker container started successfully'
        
        # Step 3: Wait for container to be ready
        task.message = 'Waiting for container to be ready...'
        task.progress = 95
        
        # Wait up to 30 seconds for container to be ready
        ready = False
        for i in range(30):
            container_status = docker.get_branch_container_status(branch_name)
            if container_status.get('status') == 'running':
                ready = True
                break
            time.sleep(1)
        
        if not ready:
            raise Exception("Container did not become ready within timeout")
        
        # Task completed successfully
        task.status = 'completed'
        task.progress = 100
        task.message = 'Branch container is ready'
        task.completed_at = datetime.utcnow().isoformat() + 'Z'
        task.result = {
            'container_status': 'running',
            'port': branch_info.get('port') if branch_info else None
        }
        
        # Update branch status
        if branch_info:
            branch_info['status'] = 'running'
            branch_info['container_started'] = True
            branch_info['build_completed_at'] = task.completed_at
            utils.save_branch_info(branch_name, branch_info)
        
        logger.info(f"Background build task {task_id} completed successfully for branch {branch_name}")
        
    except Exception as e:
        # Task failed
        task.status = 'failed'
        task.error = str(e)
        task.message = f'Build failed: {str(e)}'
        task.completed_at = datetime.utcnow().isoformat() + 'Z'
        
        # Update branch status
        branch_info = utils.get_branch_info(branch_name)
        if branch_info:
            branch_info['status'] = 'build_failed'
            branch_info['build_error'] = str(e)
            utils.save_branch_info(branch_name, branch_info)
        
        logger.error(f"Background build task {task_id} failed for branch {branch_name}: {e}")

def get_task_status(task_id):
    """Get the status of a background task"""
    if task_id not in background_tasks:
        return None
    return background_tasks[task_id]

def get_branch_build_status(branch_name):
    """Get the build status for a specific branch"""
    # Find the most recent build task for this branch
    for task_id, task in background_tasks.items():
        if task.branch_name == branch_name and task.task_type == 'branch_build':
            return task
    
    # If no task found, check if branch exists and return its status
    branch_info = utils.get_branch_info(branch_name)
    if branch_info:
        return {
            'status': branch_info.get('status', 'unknown'),
            'message': f"Branch status: {branch_info.get('status', 'unknown')}",
            'branch_info': branch_info
        }
    
    return None

def cleanup_completed_tasks(max_age_hours=24):
    """Clean up old completed tasks to prevent memory leaks"""
    cutoff_time = time.time() - (max_age_hours * 3600)
    
    tasks_to_remove = []
    for task_id, task in background_tasks.items():
        if task.completed_at:
            # Parse the ISO timestamp
            try:
                task_time = datetime.fromisoformat(task.completed_at.replace('Z', '+00:00'))
                if task_time.timestamp() < cutoff_time:
                    tasks_to_remove.append(task_id)
            except:
                # If we can't parse the timestamp, remove the task
                tasks_to_remove.append(task_id)
    
    for task_id in tasks_to_remove:
        del background_tasks[task_id]
    
    if tasks_to_remove:
        logger.info(f"Cleaned up {len(tasks_to_remove)} old background tasks") 