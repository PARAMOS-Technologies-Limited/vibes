import os
import json
import shutil
import logging
from datetime import datetime
from . import gemini

logger = logging.getLogger(__name__)

def duplicate_app_directory(branch_name, port, api_key=None, services=None):
    """Duplicate the app directory for the new branch"""
    try:
        # Get template directory from environment variable or use default
        template_dir = os.getenv('APP_TEMPLATE_PATH', '/opt/hovel-templates/app-template')
        target_dir = f'branches/{branch_name}'
        
        # Validate template directory exists
        if not os.path.exists(template_dir):
            logger.error(f"Template directory not found: {template_dir}")
            raise FileNotFoundError(f"Template directory not found: {template_dir}")
        
        # Remove existing directory if it exists
        if os.path.exists(target_dir):
            shutil.rmtree(target_dir)
        
        # Copy the template directory
        shutil.copytree(template_dir, target_dir)
        logger.info(f"Duplicated app directory from {template_dir} to {target_dir}")
        
        # Create branch-specific environment file
        create_branch_env_file(branch_name, target_dir, port, api_key)
        
        # Create branch-specific Docker Compose file
        create_branch_docker_compose(branch_name, target_dir, port, services)
        
        # Create branch-specific Gemini config if API key is provided
        if api_key:
            gemini.create_branch_gemini_settings(branch_name, target_dir, api_key)
        
        return target_dir
    except Exception as e:
        logger.error(f"Error duplicating app directory: {e}")
        raise

def create_branch_env_file(branch_name, target_dir, port, api_key=None):
    """Create environment file for the branch"""
    try:
        env_content = f"""# Environment variables for branch: {branch_name}
FLASK_APP=app.py
FLASK_ENV=development
PORT={port}
BRANCH_NAME={branch_name}
"""
        
        # Add Gemini API key if provided
        if api_key:
            env_content += f"GEMINI_API_KEY={api_key}\n"
        
        env_file = os.path.join(target_dir, '.env')
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        logger.info(f"Created environment file: {env_file}")
    except Exception as e:
        logger.warning(f"Could not create environment file: {e}")

def create_branch_docker_compose(branch_name, target_dir, port, services=None):
    """Create Docker Compose file for the branch using template"""
    try:
        # Get template directory path
        template_dir = os.getenv('APP_TEMPLATE_PATH', '/opt/hovel-templates/app-template')
        
        # Read the template file from the template directory
        template_path = os.path.join(template_dir, 'docker-compose.branch.template.yaml')
        if not os.path.exists(template_path):
            logger.warning(f"Template file not found: {template_path}")
            return
        
        with open(template_path, 'r') as f:
            template_content = f.read()
        
        # Calculate TTYD port (branch port + 1000)
        ttyd_port = port + 1000
        
        # Replace placeholders with actual values
        compose_content = template_content.replace('{{BRANCH_NAME}}', branch_name)
        compose_content = compose_content.replace('{{PORT}}', str(port))
        compose_content = compose_content.replace('{{PORT_TTYD}}', str(ttyd_port))
        
        # If services are specified, filter the Docker Compose content to include only those services
        if services and isinstance(services, list):
            compose_content = filter_docker_compose_services(compose_content, services)
        
        compose_file = os.path.join(target_dir, 'docker-compose.yaml')
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        logger.info(f"Created Docker Compose file from template: {compose_file}")
        if services:
            logger.info(f"Filtered to include services: {services}")
    except Exception as e:
        logger.warning(f"Could not create Docker Compose file: {e}")

def filter_docker_compose_services(compose_content, services):
    """Filter Docker Compose content to include only specified services"""
    try:
        import yaml
        
        # Parse the YAML content
        compose_data = yaml.safe_load(compose_content)
        
        if not compose_data or 'services' not in compose_data:
            return compose_content
        
        # Filter services
        original_services = compose_data['services']
        filtered_services = {}
        
        for service_name in services:
            if service_name in original_services:
                filtered_services[service_name] = original_services[service_name]
            else:
                logger.warning(f"Service '{service_name}' not found in Docker Compose template")
        
        # Update the compose data with filtered services
        compose_data['services'] = filtered_services
        
        # Convert back to YAML
        return yaml.dump(compose_data, default_flow_style=False, sort_keys=False)
        
    except ImportError:
        logger.warning("PyYAML not available, using string-based filtering")
        return filter_docker_compose_services_string(compose_content, services)
    except Exception as e:
        logger.warning(f"Error filtering Docker Compose services: {e}")
        return compose_content

def filter_docker_compose_services_string(compose_content, services):
    """Fallback string-based filtering for Docker Compose services"""
    try:
        lines = compose_content.split('\n')
        filtered_lines = []
        in_services_section = False
        current_service = None
        include_current_service = False
        indent_level = 0
        
        for line in lines:
            stripped_line = line.strip()
            
            # Check if we're entering the services section
            if stripped_line == 'services:':
                in_services_section = True
                filtered_lines.append(line)
                continue
            
            # If we're not in services section, include all lines
            if not in_services_section:
                filtered_lines.append(line)
                continue
            
            # Calculate indent level
            indent_level = len(line) - len(line.lstrip())
            
            # Check if this is a service definition (top level in services)
            if in_services_section and indent_level == 2 and stripped_line and not stripped_line.startswith('#'):
                current_service = stripped_line.rstrip(':')
                include_current_service = current_service in services
                
                if include_current_service:
                    filtered_lines.append(line)
                continue
            
            # Include lines that belong to included services
            if include_current_service:
                filtered_lines.append(line)
            # If we encounter a line with same or less indent as service definition, we're done with this service
            elif in_services_section and indent_level <= 2 and stripped_line and not stripped_line.startswith('#'):
                # This might be another service or end of services section
                if stripped_line == 'networks:' or stripped_line == 'volumes:' or stripped_line == 'configs:':
                    # End of services section
                    in_services_section = False
                    filtered_lines.append(line)
                else:
                    # Another service
                    current_service = stripped_line.rstrip(':')
                    include_current_service = current_service in services
                    if include_current_service:
                        filtered_lines.append(line)
        
        return '\n'.join(filtered_lines)
        
    except Exception as e:
        logger.warning(f"Error in string-based filtering: {e}")
        return compose_content

def create_branch_config(branch_name, port, app_dir):
    """Create configuration for the new branch"""
    config = {
        'branch_name': branch_name,
        'port': port,
        'app_directory': app_dir,
        'created_at': datetime.utcnow().isoformat() + 'Z',
        'status': 'created'
    }
    
    # Save config to file
    config_file = f'branches/{branch_name}/branch_config.json'
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Note: Docker Compose file is already created by create_branch_docker_compose function
    
    return config 