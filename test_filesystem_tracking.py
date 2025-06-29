#!/usr/bin/env python3
"""
Test script for filesystem-based branch tracking
This script tests the new filesystem-based branch tracking system.
"""

import os
import json
import requests
import time
import subprocess

def test_filesystem_tracking():
    """Test the filesystem-based branch tracking system"""
    
    print("🧪 Testing Filesystem-Based Branch Tracking")
    print("=" * 50)
    
    # Test 1: Check if server is running
    print("\n1. Checking if server is running...")
    try:
        response = requests.get('http://localhost:8000/health', timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
        else:
            print("❌ Server is not responding correctly")
            return False
    except requests.exceptions.RequestException:
        print("❌ Server is not running. Please start the server first.")
        return False
    
    # Test 2: List existing branches
    print("\n2. Listing existing branches...")
    try:
        response = requests.get('http://localhost:8000/api/branches')
        if response.status_code == 200:
            branches = response.json()
            print(f"✅ Found {branches['count']} existing branches")
            for branch in branches['branches']:
                print(f"   - {branch['branch_name']} (port: {branch['port']}, status: {branch['status']})")
        else:
            print(f"❌ Failed to list branches: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
    
    # Test 3: Create a test branch
    print("\n3. Creating test branch...")
    test_branch_name = f"test-fs-tracking-{int(time.time())}"
    
    try:
        response = requests.post('http://localhost:8000/api/branch', 
                               json={
                                   'branch_name': test_branch_name,
                                   'gemini_api_key': 'test-api-key-for-config'
                               })
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created branch: {test_branch_name}")
            print(f"   Port: {result['port']}")
            print(f"   Directory: {result['app_directory']}")
            print(f"   Status: {result['status']}")
        else:
            print(f"❌ Failed to create branch: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error creating branch: {e}")
        return False
    
    # Test 4: Verify .branch file was created
    print("\n4. Verifying .branch file creation...")
    branch_file = f'branches/{test_branch_name}/.branch'
    if os.path.exists(branch_file):
        print(f"✅ .branch file exists: {branch_file}")
        try:
            with open(branch_file, 'r') as f:
                branch_info = json.load(f)
            print(f"   Branch info: {json.dumps(branch_info, indent=2)}")
        except Exception as e:
            print(f"❌ Error reading .branch file: {e}")
    else:
        print(f"❌ .branch file not found: {branch_file}")
        return False
    
    # Test 5: List branches again to verify the new branch appears
    print("\n5. Listing branches after creation...")
    try:
        response = requests.get('http://localhost:8000/api/branches')
        if response.status_code == 200:
            branches = response.json()
            print(f"✅ Found {branches['count']} branches after creation")
            
            # Check if our test branch is in the list
            test_branch_found = False
            for branch in branches['branches']:
                if branch['branch_name'] == test_branch_name:
                    test_branch_found = True
                    print(f"✅ Test branch found in list: {branch['branch_name']} (port: {branch['port']})")
                    break
            
            if not test_branch_found:
                print("❌ Test branch not found in branch list")
                return False
        else:
            print(f"❌ Failed to list branches: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
    
    # Test 6: Get branch status
    print("\n6. Getting branch status...")
    try:
        response = requests.get(f'http://localhost:8000/api/branch/{test_branch_name}/status')
        if response.status_code == 200:
            status = response.json()
            print(f"✅ Branch status: {status['container_status']['status']}")
            print(f"   Port: {status['port']}")
        else:
            print(f"❌ Failed to get branch status: {response.status_code}")
    except Exception as e:
        print(f"❌ Error getting branch status: {e}")
    
    # Test 7: Delete the test branch
    print("\n7. Cleaning up test branch...")
    try:
        response = requests.delete(f'http://localhost:8000/api/branch/{test_branch_name}')
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Deleted branch: {test_branch_name}")
            print(f"   Actions: {result['actions_performed']}")
        else:
            print(f"❌ Failed to delete branch: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"❌ Error deleting branch: {e}")
    
    # Test 8: Verify .branch file was removed
    print("\n8. Verifying .branch file removal...")
    if not os.path.exists(branch_file):
        print(f"✅ .branch file removed: {branch_file}")
    else:
        print(f"❌ .branch file still exists: {branch_file}")
    
    # Test 9: List branches one more time
    print("\n9. Final branch list...")
    try:
        response = requests.get('http://localhost:8000/api/branches')
        if response.status_code == 200:
            branches = response.json()
            print(f"✅ Final branch count: {branches['count']}")
            
            # Check that our test branch is no longer in the list
            test_branch_found = False
            for branch in branches['branches']:
                if branch['branch_name'] == test_branch_name:
                    test_branch_found = True
                    print(f"❌ Test branch still found in list (should be deleted)")
                    break
            
            if not test_branch_found:
                print("✅ Test branch properly removed from list")
        else:
            print(f"❌ Failed to list branches: {response.status_code}")
    except Exception as e:
        print(f"❌ Error listing branches: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Filesystem-based branch tracking test completed!")
    return True

def test_server_restart_persistence():
    """Test that branches persist across server restarts"""
    
    print("\n🔄 Testing Server Restart Persistence")
    print("=" * 50)
    
    # Create a persistent test branch
    persistent_branch_name = f"persistent-test-{int(time.time())}"
    
    print(f"\n1. Creating persistent test branch: {persistent_branch_name}")
    try:
        response = requests.post('http://localhost:8000/api/branch', 
                               json={
                                   'branch_name': persistent_branch_name,
                                   'gemini_api_key': 'test-api-key-for-config'
                               })
        
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Created persistent branch: {persistent_branch_name}")
            print(f"   Port: {result['port']}")
        else:
            print(f"❌ Failed to create persistent branch: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error creating persistent branch: {e}")
        return False
    
    # Verify .branch file exists
    branch_file = f'branches/{persistent_branch_name}/.branch'
    if not os.path.exists(branch_file):
        print(f"❌ .branch file not found: {branch_file}")
        return False
    
    print(f"\n2. .branch file exists: {branch_file}")
    
    # Simulate server restart by calling the initialization function
    print("\n3. Simulating server restart...")
    try:
        # Import the server module to test initialization
        import sys
        sys.path.append('.')
        from server import initialize_branch_system, get_all_branches
        
        # Test initialization
        initialize_branch_system()
        
        # Check if branch is still found
        branches = get_all_branches()
        if persistent_branch_name in branches:
            print(f"✅ Persistent branch found after restart simulation: {persistent_branch_name}")
            print(f"   Port: {branches[persistent_branch_name]['port']}")
        else:
            print(f"❌ Persistent branch not found after restart simulation")
            return False
    except Exception as e:
        print(f"❌ Error testing restart persistence: {e}")
        return False
    
    # Clean up
    print(f"\n4. Cleaning up persistent test branch...")
    try:
        response = requests.delete(f'http://localhost:8000/api/branch/{persistent_branch_name}')
        if response.status_code == 200:
            print(f"✅ Deleted persistent branch: {persistent_branch_name}")
        else:
            print(f"❌ Failed to delete persistent branch: {response.status_code}")
    except Exception as e:
        print(f"❌ Error deleting persistent branch: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Server restart persistence test completed!")
    return True

if __name__ == '__main__':
    print("🚀 Starting Filesystem-Based Branch Tracking Tests")
    print("Make sure the server is running on http://localhost:8000")
    print("=" * 60)
    
    # Run the main test
    success1 = test_filesystem_tracking()
    
    # Run the persistence test
    success2 = test_server_restart_persistence()
    
    print("\n" + "=" * 60)
    if success1 and success2:
        print("🎉 All tests passed! Filesystem-based tracking is working correctly.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    
    print("\n📋 Test Summary:")
    print("- Filesystem-based branch tracking: " + ("✅ PASS" if success1 else "❌ FAIL"))
    print("- Server restart persistence: " + ("✅ PASS" if success2 else "❌ FAIL")) 