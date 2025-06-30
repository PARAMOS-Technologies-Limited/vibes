#!/usr/bin/env python3
"""
Test script for the new Gemini session endpoint
"""

import requests
import json
import time

def test_gemini_session_endpoint():
    """Test the new Gemini session endpoint"""
    
    # Configuration
    base_url = "http://localhost:8000"
    test_branch = "test-gemini-session"
    
    print("🧪 Testing Gemini Session Endpoint")
    print("=" * 50)
    
    # Step 1: Create a test branch
    print(f"\n1. Creating test branch: {test_branch}")
    create_data = {
        "branch_name": test_branch,
        "gemini_api_key": "test-key-12345",  # This will be validated
        "auto_start": True
    }
    
    try:
        response = requests.post(f"{base_url}/api/branch", json=create_data)
        print(f"   Status: {response.status_code}")
        
        if response.status_code in [201, 202]:
            print("   ✅ Branch created successfully")
            branch_data = response.json()
            print(f"   Branch port: {branch_data.get('port')}")
        else:
            print(f"   ❌ Failed to create branch: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Step 2: Wait for branch to be ready
    print(f"\n2. Waiting for branch to be ready...")
    max_wait = 60  # 60 seconds
    wait_time = 0
    
    while wait_time < max_wait:
        try:
            status_response = requests.get(f"{base_url}/api/branch/{test_branch}/status")
            if status_response.status_code == 200:
                status_data = status_response.json()
                container_status = status_data.get('container_status', {}).get('status')
                
                if container_status == 'running':
                    print("   ✅ Branch container is running")
                    break
                elif container_status == 'error':
                    print("   ❌ Branch container failed to start")
                    return False
                else:
                    print(f"   ⏳ Container status: {container_status}")
                    
            time.sleep(2)
            wait_time += 2
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Status check failed: {e}")
            return False
    
    if wait_time >= max_wait:
        print("   ❌ Timeout waiting for branch to be ready")
        return False
    
    # Step 3: Start Gemini session
    print(f"\n3. Starting Gemini session...")
    try:
        session_response = requests.post(f"{base_url}/api/branch/{test_branch}/gemini-session")
        print(f"   Status: {session_response.status_code}")
        
        if session_response.status_code == 200:
            session_data = session_response.json()
            print("   ✅ Gemini session started successfully")
            print(f"   TTYD Port: {session_data.get('ttyd_port')}")
            print(f"   Access URL: {session_data.get('access_url')}")
            print(f"   Instructions: {session_data.get('instructions')}")
            
            # Verify the session details are saved in branch info
            branch_response = requests.get(f"{base_url}/api/branch/{test_branch}/status")
            if branch_response.status_code == 200:
                branch_info = branch_response.json()
                ttyd_session = branch_info.get('ttyd_session')
                if ttyd_session:
                    print("   ✅ TTYD session info saved to branch metadata")
                else:
                    print("   ⚠️  TTYD session info not found in branch metadata")
            
        else:
            print(f"   ❌ Failed to start Gemini session: {session_response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
        return False
    
    # Step 4: Test error cases
    print(f"\n4. Testing error cases...")
    
    # Test with non-existent branch
    try:
        error_response = requests.post(f"{base_url}/api/branch/non-existent-branch/gemini-session")
        if error_response.status_code == 404:
            print("   ✅ Correctly returns 404 for non-existent branch")
        else:
            print(f"   ⚠️  Unexpected status for non-existent branch: {error_response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Error test failed: {e}")
    
    # Step 5: Cleanup
    print(f"\n5. Cleaning up test branch...")
    try:
        cleanup_response = requests.delete(f"{base_url}/api/branch/{test_branch}")
        if cleanup_response.status_code == 200:
            print("   ✅ Test branch cleaned up successfully")
        else:
            print(f"   ⚠️  Cleanup failed: {cleanup_response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   ⚠️  Cleanup request failed: {e}")
    
    print(f"\n🎉 Gemini session endpoint test completed!")
    return True

if __name__ == "__main__":
    test_gemini_session_endpoint() 