#!/usr/bin/env python3
"""
Test script to verify the external template directory functionality.
This script tests that branches can be created using the external template.
"""

import os
import sys
import json
import shutil
import requests
import time
from pathlib import Path

def test_template_functionality():
    """Test the external template functionality"""
    
    print("🧪 Testing External Template Functionality")
    print("=" * 50)
    
    # Check if template directory exists
    template_dir = Path('/opt/hovel-templates/app-template')
    if not template_dir.exists():
        print(f"❌ Template directory not found: {template_dir}")
        print("Please run setup_template_directory.py first")
        return False
    
    print(f"✅ Template directory found: {template_dir}")
    
    # List template files
    print("\n📁 Template files:")
    for file_path in template_dir.rglob('*'):
        if file_path.is_file():
            relative_path = file_path.relative_to(template_dir)
            print(f"  - {relative_path}")
    
    # Test API server connectivity
    print("\n🔌 Testing API server connectivity...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ API server is running")
        else:
            print(f"⚠️  API server responded with status: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"❌ Cannot connect to API server: {e}")
        print("Please make sure the Docker container is running")
        return False
    
    # Create a test branch
    test_branch_name = f"test-template-{int(time.time())}"
    print(f"\n🚀 Creating test branch: {test_branch_name}")
    
    try:
        response = requests.post(
            'http://localhost:8000/api/branch',
            headers={'Content-Type': 'application/json'},
            json={'branch_name': test_branch_name},
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Branch created successfully")
            print(f"   Port: {result.get('data', {}).get('port', 'N/A')}")
            print(f"   Directory: {result.get('data', {}).get('app_directory', 'N/A')}")
        else:
            print(f"❌ Failed to create branch: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Error creating branch: {e}")
        return False
    
    # Verify branch directory was created with template files
    branch_dir = Path(f'branches/{test_branch_name}')
    if not branch_dir.exists():
        print(f"❌ Branch directory not created: {branch_dir}")
        return False
    
    print(f"\n📁 Verifying branch directory: {branch_dir}")
    
    # Check for expected files
    expected_files = [
        'app.js',
        'package.json', 
        'Dockerfile',
        'docker-compose.yaml',
        '.env'
    ]
    
    missing_files = []
    for file_name in expected_files:
        file_path = branch_dir / file_name
        if file_path.exists():
            print(f"  ✅ {file_name}")
        else:
            print(f"  ❌ {file_name} (missing)")
            missing_files.append(file_name)
    
    if missing_files:
        print(f"\n❌ Missing files in branch directory: {missing_files}")
        return False
    
    # Verify .env file has correct port
    env_file = branch_dir / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            env_content = f.read()
            if 'PORT=' in env_content:
                print(f"  ✅ .env file contains PORT configuration")
            else:
                print(f"  ❌ .env file missing PORT configuration")
    
    # Verify docker-compose.yaml has correct placeholders replaced
    compose_file = branch_dir / 'docker-compose.yaml'
    if compose_file.exists():
        with open(compose_file, 'r') as f:
            compose_content = f.read()
            if test_branch_name in compose_content and '{{BRANCH_NAME}}' not in compose_content:
                print(f"  ✅ docker-compose.yaml has placeholders replaced")
            else:
                print(f"  ❌ docker-compose.yaml placeholders not replaced correctly")
    
    # Clean up test branch
    print(f"\n🧹 Cleaning up test branch: {test_branch_name}")
    try:
        response = requests.delete(f'http://localhost:8000/api/branch/{test_branch_name}', timeout=10)
        if response.status_code == 200:
            print("✅ Test branch cleaned up successfully")
        else:
            print(f"⚠️  Could not clean up test branch: {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"⚠️  Error cleaning up test branch: {e}")
    
    print("\n🎉 External template functionality test completed successfully!")
    return True

def check_template_environment():
    """Check the template environment setup"""
    
    print("🔍 Checking Template Environment")
    print("=" * 40)
    
    # Check environment variable
    template_path = os.getenv('APP_TEMPLATE_PATH')
    if template_path:
        print(f"✅ APP_TEMPLATE_PATH set to: {template_path}")
    else:
        print("❌ APP_TEMPLATE_PATH not set")
        return False
    
    # Check if path exists
    if os.path.exists(template_path):
        print(f"✅ Template path exists: {template_path}")
    else:
        print(f"❌ Template path does not exist: {template_path}")
        return False
    
    # Check Docker volume mount
    docker_compose_file = Path('docker-compose.yaml')
    if docker_compose_file.exists():
        with open(docker_compose_file, 'r') as f:
            content = f.read()
            if '/opt/hovel-templates:/opt/hovel-templates' in content:
                print("✅ Docker volume mount configured")
            else:
                print("❌ Docker volume mount not configured")
                return False
    else:
        print("❌ docker-compose.yaml not found")
        return False
    
    return True

if __name__ == "__main__":
    print("🧪 Hovel External Template Test Suite")
    print("=" * 50)
    
    # Check environment first
    if not check_template_environment():
        print("\n❌ Environment check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n" + "=" * 50)
    
    # Run functionality test
    if test_template_functionality():
        print("\n✅ All tests passed! External template functionality is working correctly.")
        sys.exit(0)
    else:
        print("\n❌ Tests failed. Please check the issues above.")
        sys.exit(1) 