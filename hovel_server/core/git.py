import subprocess
import logging

logger = logging.getLogger(__name__)

def create_git_branch(branch_name):
    """Create a new git branch in the app directory"""
    try:
        # Check if we're in a git repository in the app directory
        result = subprocess.run(['git', 'status'], capture_output=True, text=True, cwd='app')
        if result.returncode != 0:
            logger.warning("Not in a git repository in app directory or git not available - skipping git branch creation")
            return True
        
        # Create and checkout new branch in the app directory
        subprocess.run(['git', 'checkout', '-b', branch_name], check=True, cwd='app')
        logger.info(f"Created and checked out branch: {branch_name} in app directory")
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