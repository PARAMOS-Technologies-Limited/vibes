import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Configuration
BASE_PORT = 8000

def get_branch_info(branch_name):
    """Get branch information from the .branch file"""
    try:
        branch_file = f'branches/{branch_name}/.branch'
        if os.path.exists(branch_file):
            with open(branch_file, 'r') as f:
                return json.load(f)
        return None
    except Exception as e:
        logger.error(f"Error reading branch info for {branch_name}: {e}")
        return None

def save_branch_info(branch_name, branch_info):
    """Save branch information to the .branch file"""
    try:
        branch_file = f'branches/{branch_name}/.branch'
        os.makedirs(os.path.dirname(branch_file), exist_ok=True)
        with open(branch_file, 'w') as f:
            json.dump(branch_info, f, indent=2)
        logger.info(f"Saved branch info to {branch_file}")
    except Exception as e:
        logger.error(f"Error saving branch info for {branch_name}: {e}")
        raise

def get_all_branches():
    """Scan the filesystem to get all existing branches"""
    branches = {}
    try:
        if not os.path.exists('branches'):
            return branches
        
        for branch_name in os.listdir('branches'):
            branch_dir = f'branches/{branch_name}'
            if os.path.isdir(branch_dir):
                branch_info = get_branch_info(branch_name)
                if branch_info:
                    branches[branch_name] = branch_info
        return branches
    except Exception as e:
        logger.error(f"Error scanning branches: {e}")
        return branches

def get_next_available_port():
    """Get the next available port starting from BASE_PORT"""
    try:
        # Get all existing branches and their ports
        branches = get_all_branches()
        used_ports = {branch_info.get('port', 0) for branch_info in branches.values()}
        
        port = BASE_PORT + 1
        while port in used_ports:
            port += 1
        return port
    except Exception as e:
        logger.error(f"Error getting next available port: {e}")
        # Fallback to simple increment
        return BASE_PORT + 1

def branch_exists(branch_name):
    """Check if a branch exists by looking for its .branch file"""
    try:
        branch_file = f'branches/{branch_name}/.branch'
        return os.path.exists(branch_file)
    except Exception as e:
        logger.error(f"Error checking if branch {branch_name} exists: {e}")
        return False

def initialize_branch_system():
    """Initialize the branch system by scanning for existing branches"""
    try:
        logger.info("Initializing branch system...")
        branches = get_all_branches()
        logger.info(f"Found {len(branches)} existing branches: {list(branches.keys())}")
        
        # Log details of each found branch
        for branch_name, branch_info in branches.items():
            logger.info(f"Branch: {branch_name}, Port: {branch_info.get('port')}, Status: {branch_info.get('status')}")
        
        return True
    except Exception as e:
        logger.error(f"Error initializing branch system: {e}")
        return False 