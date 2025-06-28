#!/usr/bin/env python3
"""
Branch Runner Script
This script runs a specific branch's Flask app on its assigned port.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def load_branch_config(branch_name):
    """Load configuration for a specific branch"""
    config_file = f'branches/{branch_name}/branch_config.json'
    
    if not os.path.exists(config_file):
        raise FileNotFoundError(f"Branch configuration not found for {branch_name}")
    
    with open(config_file, 'r') as f:
        return json.load(f)

def run_branch_app(branch_name):
    """Run the Flask app for a specific branch"""
    try:
        # Load branch configuration
        config = load_branch_config(branch_name)
        port = config['port']
        app_dir = config['app_directory']
        
        print(f"Starting branch '{branch_name}' on port {port}")
        print(f"App directory: {app_dir}")
        
        # Change to the branch app directory
        os.chdir(app_dir)
        
        # Check if .env file exists and load it
        env_file = os.path.join(app_dir, '.env')
        env = os.environ.copy()
        
        if os.path.exists(env_file):
            print(f"Loading environment from: {env_file}")
            with open(env_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key.strip()] = value.strip()
        
        # Set additional environment variables
        env['FLASK_APP'] = 'app.py'
        env['FLASK_ENV'] = 'development'
        env['PORT'] = str(port)
        env['BRANCH_NAME'] = branch_name
        
        print(f"Environment variables:")
        print(f"  FLASK_APP: {env.get('FLASK_APP')}")
        print(f"  FLASK_ENV: {env.get('FLASK_ENV')}")
        print(f"  PORT: {env.get('PORT')}")
        print(f"  BRANCH_NAME: {env.get('BRANCH_NAME')}")
        
        # Run the Flask app
        subprocess.run([
            sys.executable, 'app.py'
        ], env=env)
        
    except Exception as e:
        print(f"Error running branch app: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Run a branch-specific Flask app')
    parser.add_argument('branch_name', help='Name of the branch to run')
    
    args = parser.parse_args()
    
    if not args.branch_name:
        print("Error: Branch name is required")
        sys.exit(1)
    
    run_branch_app(args.branch_name)

if __name__ == '__main__':
    main() 