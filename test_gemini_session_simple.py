#!/usr/bin/env python3
"""
Simple test script for the Gemini session endpoint structure
"""

import requests
import json

def test_gemini_session_endpoint_structure():
    """Test the Gemini session endpoint structure and error handling"""
    
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Gemini Session Endpoint Structure")
    print("=" * 50)
    
    # Test 1: Try to start session on non-existent branch
    print(f"\n1. Testing with non-existent branch...")
    try:
        response = requests.post(f"{base_url}/api/branch/non-existent-branch/gemini-session")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for non-existent branch")
            response_data = response.json()
            print(f"   Error message: {response_data.get('error')}")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Check if the endpoint is registered
    print(f"\n2. Checking available endpoints...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            print("   ✅ API status endpoint accessible")
            # The endpoint list might be in the response
            print(f"   Response: {response.text[:200]}...")
        else:
            print(f"   ⚠️  API status endpoint returned: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ API status check failed: {e}")
    
    # Test 3: Test with a branch that exists but container is not running
    print(f"\n3. Testing with existing branch but stopped container...")
    
    # First, let's see what branches exist
    try:
        branches_response = requests.get(f"{base_url}/api/branches")
        if branches_response.status_code == 200:
            branches_data = branches_response.json()
            existing_branches = branches_data.get('branches', [])
            
            if existing_branches:
                # Use the first existing branch
                test_branch = existing_branches[0].get('branch_name')
                print(f"   Found existing branch: {test_branch}")
                
                # Try to start Gemini session
                session_response = requests.post(f"{base_url}/api/branch/{test_branch}/gemini-session")
                print(f"   Session start status: {session_response.status_code}")
                
                if session_response.status_code == 400:
                    print("   ✅ Correctly returns 400 when container is not running")
                    response_data = session_response.json()
                    print(f"   Error: {response_data.get('error')}")
                    print(f"   Message: {response_data.get('message')}")
                else:
                    print(f"   ⚠️  Unexpected status: {session_response.status_code}")
                    print(f"   Response: {session_response.text}")
            else:
                print("   ℹ️  No existing branches found")
        else:
            print(f"   ❌ Failed to get branches: {branches_response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    print(f"\n🎉 Gemini session endpoint structure test completed!")
    print(f"\n📝 Summary:")
    print(f"   - Endpoint: POST /api/branch/{{branch_name}}/gemini-session")
    print(f"   - Returns 404 for non-existent branches")
    print(f"   - Returns 400 when container is not running")
    print(f"   - Should return 200 with session details when successful")
    print(f"   - TTYD port = branch_port + 1000")
    print(f"   - Command: ttyd -o -W -p {{port}} gemini")

if __name__ == "__main__":
    test_gemini_session_endpoint_structure() 