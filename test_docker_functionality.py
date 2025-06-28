#!/usr/bin/env python3
"""
Test Docker Functionality
This script tests the Docker integration for branch management.
"""

import requests
import json
import time
import sys

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if the API is running"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        return False

def test_create_branch_with_auto_start():
    """Test creating a branch with auto-start enabled"""
    try:
        data = {
            "branch_name": "test-docker-auto-start",
            "auto_start": True
        }
        
        response = requests.post(
            f"{BASE_URL}/api/branch",
            json=data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created branch: {result['branch_name']}")
            print(f"   Port: {result['port']}")
            print(f"   Auto-start: {result['auto_start']}")
            print(f"   Container started: {result['container_started']}")
            return result['branch_name']
        else:
            print(f"❌ Failed to create branch: {response.status_code}")
            print(f"   Response: {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error creating branch: {e}")
        return None

def test_branch_status(branch_name):
    """Test getting branch status"""
    try:
        response = requests.get(f"{BASE_URL}/api/branch/{branch_name}/status")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Branch status: {result['container_status']['status']}")
            return result['container_status']['status']
        else:
            print(f"❌ Failed to get branch status: {response.status_code}")
            return None
    except Exception as e:
        print(f"❌ Error getting branch status: {e}")
        return None

def test_branch_logs(branch_name):
    """Test getting branch logs"""
    try:
        response = requests.get(f"{BASE_URL}/api/branch/{branch_name}/logs?lines=10")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Got branch logs ({len(result['logs'])} characters)")
            return True
        else:
            print(f"❌ Failed to get branch logs: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error getting branch logs: {e}")
        return False

def test_stop_branch(branch_name):
    """Test stopping a branch"""
    try:
        response = requests.post(f"{BASE_URL}/api/branch/{branch_name}/stop")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Stopped branch: {result['message']}")
            return True
        else:
            print(f"❌ Failed to stop branch: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error stopping branch: {e}")
        return False

def test_start_branch(branch_name):
    """Test starting a branch"""
    try:
        response = requests.post(f"{BASE_URL}/api/branch/{branch_name}/start")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Started branch: {result['message']}")
            return True
        else:
            print(f"❌ Failed to start branch: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error starting branch: {e}")
        return False

def test_list_branches():
    """Test listing all branches"""
    try:
        response = requests.get(f"{BASE_URL}/api/branches")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Listed {result['count']} branches")
            for branch in result['branches']:
                print(f"   - {branch['branch_name']} (port {branch['port']})")
            return True
        else:
            print(f"❌ Failed to list branches: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Docker Functionality for Hovel")
    print("=" * 50)
    
    # Test 1: API Health
    if not test_api_health():
        print("❌ API is not available. Please start the server first.")
        sys.exit(1)
    
    print()
    
    # Test 2: Create branch with auto-start
    branch_name = test_create_branch_with_auto_start()
    if not branch_name:
        print("❌ Failed to create test branch")
        sys.exit(1)
    
    print()
    
    # Test 3: Wait a moment for container to start
    print("⏳ Waiting for container to start...")
    time.sleep(5)
    
    # Test 4: Check branch status
    status = test_branch_status(branch_name)
    
    print()
    
    # Test 5: Get branch logs
    test_branch_logs(branch_name)
    
    print()
    
    # Test 6: Stop branch
    test_stop_branch(branch_name)
    
    print()
    
    # Test 7: Start branch again
    test_start_branch(branch_name)
    
    print()
    
    # Test 8: List all branches
    test_list_branches()
    
    print()
    print("🎉 Docker functionality tests completed!")

if __name__ == '__main__':
    main() 