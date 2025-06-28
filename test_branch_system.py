#!/usr/bin/env python3
"""
Test script for the branch management system
"""

import requests
import json
import time
import subprocess
import os

def test_branch_creation():
    """Test creating a new branch"""
    print("Testing branch creation...")
    
    # Create a test branch
    response = requests.post(
        'http://localhost:8000/api/branch',
        json={'branch_name': 'test-feature'}
    )
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Branch created successfully: {data['branch_name']}")
        print(f"   Port: {data['port']}")
        print(f"   Directory: {data['app_directory']}")
        return data
    else:
        print(f"❌ Failed to create branch: {response.text}")
        return None

def test_branch_listing():
    """Test listing branches"""
    print("\nTesting branch listing...")
    
    response = requests.get('http://localhost:8000/api/branches')
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} branches:")
        for branch in data['branches']:
            print(f"   - {branch['branch_name']} (port {branch['port']})")
        return data
    else:
        print(f"❌ Failed to list branches: {response.text}")
        return None

def test_branch_environment(branch_name):
    """Test that the branch environment was created correctly"""
    print(f"\nTesting branch environment for '{branch_name}'...")
    
    branch_dir = f'branches/{branch_name}'
    
    # Check if directory exists
    if not os.path.exists(branch_dir):
        print(f"❌ Branch directory not found: {branch_dir}")
        return False
    
    # Check for required files
    required_files = ['app.py', 'requirements.txt', '.env', 'docker-compose.yaml', 'branch_config.json']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(os.path.join(branch_dir, file)):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files found")
    
    # Check .env file content
    env_file = os.path.join(branch_dir, '.env')
    with open(env_file, 'r') as f:
        env_content = f.read()
        if 'BRANCH_NAME=' + branch_name in env_content:
            print("✅ Environment file contains correct branch name")
        else:
            print("❌ Environment file missing branch name")
            return False
    
    # Check Docker Compose file
    compose_file = os.path.join(branch_dir, 'docker-compose.yaml')
    with open(compose_file, 'r') as f:
        compose_content = f.read()
        if f'app-{branch_name}:' in compose_content:
            print("✅ Docker Compose file contains correct service name")
        else:
            print("❌ Docker Compose file missing correct service name")
            return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Testing Branch Management System")
    print("=" * 50)
    
    # Wait for server to be ready
    print("Waiting for server to be ready...")
    time.sleep(2)
    
    # Test branch creation
    branch_data = test_branch_creation()
    if not branch_data:
        return
    
    # Test branch listing
    test_branch_listing()
    
    # Test branch environment
    if test_branch_environment(branch_data['branch_name']):
        print("\n🎉 All tests passed! The branch system is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the implementation.")

if __name__ == '__main__':
    main() 