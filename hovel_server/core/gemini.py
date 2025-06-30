import os
import shutil
import requests
import logging

logger = logging.getLogger(__name__)

def create_branch_gemini_settings(branch_name, target_dir, api_key=None):
    """Copy Gemini settings directory and create settings.json (API key will be read from environment)"""
    try:
        # Source Gemini directory
        source_gemini_dir = '.gemini'
        target_gemini_dir = os.path.join(target_dir, '.gemini')
        
        # Create target directory if it doesn't exist
        os.makedirs(target_gemini_dir, exist_ok=True)
        
        # Copy all files from source Gemini directory except settings.json
        if os.path.exists(source_gemini_dir):
            for item in os.listdir(source_gemini_dir):
                source_item = os.path.join(source_gemini_dir, item)
                target_item = os.path.join(target_gemini_dir, item)
                
                # Skip settings.json as we'll create it without the API key
                if item == 'settings.json':
                    continue
                
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, target_item)
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item)
        
        # Read the template settings file
        template_settings_path = os.path.join(source_gemini_dir, 'settings.template.json')
        if os.path.exists(template_settings_path):
            with open(template_settings_path, 'r') as f:
                settings_content = f.read()
            
            # Write the settings.json file without API key (will be read from environment)
            settings_file_path = os.path.join(target_gemini_dir, 'settings.json')
            with open(settings_file_path, 'w') as f:
                f.write(settings_content)
            
            logger.info(f"Created Gemini settings file for branch {branch_name} (API key will be read from environment)")
        else:
            logger.warning(f"Gemini settings template not found: {template_settings_path}")
            
    except Exception as e:
        logger.warning(f"Could not create Gemini settings for branch {branch_name}: {e}")

def validate_gemini_api_key(api_key):
    """Validate a Gemini API key by making a test request to the Gemini API"""
    if not api_key or not api_key.strip():
        return False, "API key is required"
    
    # Test the API key with a simple request to Gemini API
    try:
        headers = {
            'Content-Type': 'application/json',
        }
        
        # Simple test payload for Gemini API
        payload = {
            "contents": [{
                "parts": [{
                    "text": "Hello, this is a test message."
                }]
            }]
        }
        
        # Make request to Gemini API to validate the key
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}',
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            return True, "API key is valid"
        elif response.status_code == 400:
            return False, "Invalid API key format"
        elif response.status_code == 403:
            return False, "Invalid API key or quota exceeded"
        else:
            return False, f"API validation failed with status {response.status_code}"
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Error validating Gemini API key: {e}")
        return False, "Failed to validate API key - network error"
    except Exception as e:
        logger.error(f"Unexpected error validating API key: {e}")
        return False, "Failed to validate API key - unexpected error" 