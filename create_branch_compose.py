#!/usr/bin/env python3
"""
Branch Docker Compose Generator
This script generates Docker Compose files for branch deployments.
"""

import os
import sys
import json
import argparse
from pathlib import Path

def load_branch_config(branch_name):
    """Load configuration for a specific branch"""
    config_file = f'branches/{branch_name}/branch_config.json'
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Branch configuration not found for {branch_name}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

def generate_docker_compose(branch_name):
    """Generate Docker Compose file for a specific branch"""
    try:
        # Load branch configuration
        config = load_branch_config(branch_name)
        port = config['port']
        
        # Read template
        template_file = 'docker-compose.branch.template.yaml'
        if not os.path.exists(template_file):
            raise FileNotFoundError(f"Template file {template_file} not found")
        
        with open(template_file, 'r') as f:
            template_content = f.read()
        
        # Replace placeholders
        compose_content = template_content.replace('{{BRANCH_NAME}}', branch_name)
        compose_content = compose_content.replace('{{PORT}}', str(port))
        
        # Write generated compose file
        compose_file = f'branches/{branch_name}/docker-compose.yaml'
        with open(compose_file, 'w') as f:
            f.write(compose_content)
        
        print(f"Generated Docker Compose file: {compose_file}")
        return compose_file
        
    except Exception as e:
        print(f"Error generating Docker Compose file: {e}")
        raise

def main():
    parser = argparse.ArgumentParser(description='Generate Docker Compose file for a branch')
    parser.add_argument('branch_name', help='Name of the branch')
    
    args = parser.parse_args()
    
    if not args.branch_name:
        print("Error: Branch name is required")
        return 1
    
    try:
        generate_docker_compose(args.branch_name)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main()) 