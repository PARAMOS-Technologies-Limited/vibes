import os
import shutil
import requests
import logging

logger = logging.getLogger(__name__)

def create_branch_gemini_config(branch_name, target_dir, api_key):
    """Copy Gemini settings directory and create config.json with the provided API key"""
    try:
        # Source Gemini directory
        source_gemini_dir = '.gemini'
        target_gemini_dir = os.path.join(target_dir, '.gemini')
        
        # Create target directory if it doesn't exist
        os.makedirs(target_gemini_dir, exist_ok=True)
        
        # Copy all files from source Gemini directory except config.json
        if os.path.exists(source_gemini_dir):
            for item in os.listdir(source_gemini_dir):
                source_item = os.path.join(source_gemini_dir, item)
                target_item = os.path.join(target_gemini_dir, item)
                
                # Skip config.json as we'll create it with the provided API key
                if item == 'config.json':
                    continue
                
                if os.path.isfile(source_item):
                    shutil.copy2(source_item, target_item)
                elif os.path.isdir(source_item):
                    shutil.copytree(source_item, target_item)
        
        # Read the template config file
        template_config_path = os.path.join(source_gemini_dir, 'config.template.json')
        if os.path.exists(template_config_path):
            with open(template_config_path, 'r') as f:
                config_content = f.read()
            
            # Replace both possible API key placeholders with the actual one
            config_content = config_content.replace('YOUR_GEMINI_API_KEY_HERE', api_key)
            config_content = config_content.replace('{{ GEMINI_API_KEY }}', api_key)
            
            # Write the new config.json file
            config_file_path = os.path.join(target_gemini_dir, 'config.json')
            with open(config_file_path, 'w') as f:
                f.write(config_content)
            
            logger.info(f"Created Gemini config file for branch {branch_name} with provided API key")
        else:
            logger.warning(f"Gemini config template not found: {template_config_path}")
            
    except Exception as e:
        logger.warning(f"Could not create Gemini config for branch {branch_name}: {e}")

def validate_gemini_api_key(api_key):
    """Validate a Gemini API key by making a test request to the Gemini API"""
    if not api_key or not api_key.strip():
        return False, "API key is required"
    
    # Allow test key for development
    if api_key == "test-api-key-for-config":
        return True, "Test API key accepted for development"
    
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