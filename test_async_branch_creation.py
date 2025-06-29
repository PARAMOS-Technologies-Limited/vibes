#!/usr/bin/env python3
"""
Test script for asynchronous branch creation
This script tests the new asynchronous branch creation with background Docker builds.
"""

import requests
import json
import time
import sys

BASE_URL = 'http://localhost:8000'

def test_async_branch_creation():
    """Test creating a branch with asynchronous Docker build"""
    print("🧪 Testing Asynchronous Branch Creation")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Checking if server is running...")
    try:
        response = requests.get(f'{BASE_URL}/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the server first.")
        return False
    
    # Test 2: Create a branch with auto_start=True (should return 202)
    print("\n2. Creating branch with auto_start=True...")
    test_branch_name = f"async-test-{int(time.time())}"
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/branch',
            json={
                'branch_name': test_branch_name,
                'auto_start': True,
                'gemini_api_key': 'test-api-key-for-config'
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 202:
            result = response.json()
            print(f"✅ Branch creation accepted (202): {test_branch_name}")
            print(f"   Port: {result['port']}")
            print(f"   Build Task ID: {result['build_task_id']}")
            print(f"   Status: {result['status']}")
            
            task_id = result['build_task_id']
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating branch: {e}")
        return False
    
    # Test 3: Monitor build progress
    print("\n3. Monitoring build progress...")
    max_wait_time = 120  # 2 minutes
    start_time = time.time()
    
    while time.time() - start_time < max_wait_time:
        try:
            response = requests.get(f'{BASE_URL}/api/branch/{test_branch_name}/build-status')
            
            if response.status_code == 200:
                status = response.json()
                current_status = status['status']
                progress = status.get('progress', 0)
                message = status.get('message', '')
                
                print(f"   Status: {current_status} ({progress}%) - {message}")
                
                if current_status == 'completed':
                    print("✅ Build completed successfully!")
                    break
                elif current_status == 'failed':
                    print(f"❌ Build failed: {status.get('error', 'Unknown error')}")
                    return False
                elif current_status == 'building':
                    # Continue monitoring
                    time.sleep(2)
                else:
                    print(f"   Unknown status: {current_status}")
                    time.sleep(2)
            else:
                print(f"❌ Failed to get build status: {response.status_code}")
                time.sleep(2)
        except Exception as e:
            print(f"❌ Error checking build status: {e}")
            time.sleep(2)
    else:
        print("❌ Build timed out after 2 minutes")
        return False
    
    # Test 4: Verify branch is running
    print("\n4. Verifying branch is running...")
    try:
        response = requests.get(f'{BASE_URL}/api/branch/{test_branch_name}/status')
        
        if response.status_code == 200:
            status = response.json()
            container_status = status.get('container_status', {})
            
            if container_status.get('status') == 'running':
                print("✅ Branch container is running")
                print(f"   Port: {status.get('port')}")
            else:
                print(f"❌ Container not running: {container_status}")
                return False
        else:
            print(f"❌ Failed to get branch status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking branch status: {e}")
        return False
    
    # Test 5: Test the branch endpoint
    print("\n5. Testing branch endpoint...")
    try:
        port = status.get('port')
        if port:
            branch_response = requests.get(f'http://localhost:{port}/', timeout=5)
            if branch_response.status_code == 200:
                branch_data = branch_response.json()
                print(f"✅ Branch endpoint responding: {branch_data.get('message', '')}")
                print(f"   Branch name: {branch_data.get('branch', '')}")
            else:
                print(f"❌ Branch endpoint not responding correctly: {branch_response.status_code}")
        else:
            print("❌ No port found for branch")
    except Exception as e:
        print(f"❌ Error testing branch endpoint: {e}")
    
    # Test 6: Clean up
    print("\n6. Cleaning up test branch...")
    try:
        response = requests.delete(f'{BASE_URL}/api/branch/{test_branch_name}')
        
        if response.status_code == 200:
            print("✅ Test branch cleaned up successfully")
        else:
            print(f"❌ Failed to cleanup branch: {response.status_code}")
    except Exception as e:
        print(f"❌ Error cleaning up branch: {e}")
    
    print("\n🎉 Asynchronous branch creation test completed successfully!")
    return True

def test_sync_branch_creation():
    """Test creating a branch with auto_start=False (should return 201)"""
    print("\n🧪 Testing Synchronous Branch Creation (auto_start=False)")
    print("=" * 50)
    
    test_branch_name = f"sync-test-{int(time.time())}"
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/branch',
            json={
                'branch_name': test_branch_name,
                'auto_start': False,
                'gemini_api_key': 'test-api-key-for-config'
            },
            headers={'Content-Type': 'application/json'}
        )
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Branch created (201): {test_branch_name}")
            print(f"   Port: {result['port']}")
            print(f"   Status: {result['status']}")
            print(f"   Build Task ID: {result['build_task_id']}")
            
            # Clean up
            requests.delete(f'{BASE_URL}/api/branch/{test_branch_name}')
            print("✅ Sync test branch cleaned up")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error in sync test: {e}")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing Asynchronous Branch Creation System")
    print("=" * 60)
    
    # Test async creation
    if not test_async_branch_creation():
        print("❌ Async branch creation test failed")
        sys.exit(1)
    
    # Test sync creation
    if not test_sync_branch_creation():
        print("❌ Sync branch creation test failed")
        sys.exit(1)
    
    print("\n🎉 All tests passed! Asynchronous branch creation is working correctly.")

if __name__ == '__main__':
    main() 