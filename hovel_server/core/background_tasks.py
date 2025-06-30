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

    def update_status(self, status, message):
        self.status = status
        self.message = message
        if status == 'building':
            self.started_at = datetime.utcnow().isoformat() + 'Z'
        elif status == 'completed':
            self.completed_at = datetime.utcnow().isoformat() + 'Z'
        elif status == 'failed':
            self.error = message

def start_branch_build_task(branch_name, services=None):
    """Start a background task to build and start a Docker container for a branch"""
    task_id = f"build_{branch_name}_{int(time.time())}"
    
    # Create task object
    task = BackgroundTask(task_id, 'branch_build', branch_name)
    background_tasks[task_id] = task
    
    # Start background thread
    thread = threading.Thread(
        target=_build_branch_container,
        args=(task_id, branch_name, services),
        daemon=True
    )
    thread.start()
    
    return task_id

def _build_branch_container(task_id, branch_name, services=None):
    """Background task to build and start a branch container"""
    try:
        task = background_tasks.get(task_id)
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        task.update_status('building', 'Building Docker image...')
        
        # Build the Docker image
        success = docker.build_branch_image(branch_name)
        if not success:
            task.update_status('failed', 'Failed to build Docker image')
            return
        
        task.update_status('starting', 'Starting Docker container...')
        
        # Start the container
        success = docker.start_branch_container(branch_name, services)
        if not success:
            task.update_status('failed', 'Failed to start Docker container')
            return
        
        task.update_status('completed', 'Branch container started successfully')
        
        # Update branch info
        branch_info = utils.get_branch_info(branch_name)
        if branch_info:
            branch_info['status'] = 'running'
            branch_info['container_started'] = True
            if services:
                branch_info['started_services'] = services
            utils.save_branch_info(branch_name, branch_info)
        
        logger.info(f"Background build task {task_id} completed successfully")
        
    except Exception as e:
        logger.error(f"Error in background build task {task_id}: {e}")
        task = background_tasks.get(task_id)
        if task:
            task.update_status('failed', f'Build failed: {str(e)}')

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