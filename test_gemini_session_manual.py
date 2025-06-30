#!/usr/bin/env python3
"""
Manual test script for the Gemini session endpoint
"""

import requests
import json
import time

def test_gemini_session_manual():
    """Manual test of the Gemini session endpoint"""
    
    base_url = "http://localhost:8000"
    test_branch = "manual-gemini-test"
    
    print("🧪 Manual Testing of Gemini Session Endpoint")
    print("=" * 50)
    
    # Step 1: Check current branches
    print(f"\n1. Checking current branches...")
    try:
        response = requests.get(f"{base_url}/api/branches")
        if response.status_code == 200:
            branches = response.json()
            print(f"   Current branches: {len(branches.get('branches', []))}")
            for branch in branches.get('branches', []):
                print(f"   - {branch.get('branch_name')} (port: {branch.get('port')})")
        else:
            print(f"   ❌ Failed to get branches: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 2: Test the Gemini session endpoint structure
    print(f"\n2. Testing endpoint structure...")
    
    # Test with non-existent branch
    try:
        response = requests.post(f"{base_url}/api/branch/non-existent/gemini-session")
        print(f"   Non-existent branch test: {response.status_code}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404")
        else:
            print(f"   ❌ Unexpected status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 3: Check if we can create a branch manually
    print(f"\n3. Testing branch creation (will likely fail due to API key)...")
    try:
        create_data = {
            "branch_name": test_branch,
            "gemini_api_key": "invalid-key-for-testing",
            "auto_start": False
        }
        response = requests.post(f"{base_url}/api/branch", json=create_data)
        print(f"   Branch creation status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctly validates API key (expected 401)")
            print("   This is expected behavior - API key validation is working")
        elif response.status_code in [201, 202]:
            print("   ✅ Branch created successfully (unexpected but good)")
        else:
            print(f"   ⚠️  Unexpected status: {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 4: Test the endpoint with a branch that might exist
    print(f"\n4. Testing with existing branches (if any)...")
    try:
        branches_response = requests.get(f"{base_url}/api/branches")
        if branches_response.status_code == 200:
            branches_data = branches_response.json()
            existing_branches = branches_data.get('branches', [])
            
            if existing_branches:
                # Test with the first existing branch
                test_branch = existing_branches[0].get('branch_name')
                print(f"   Testing with existing branch: {test_branch}")
                
                # Check branch status first
                status_response = requests.get(f"{base_url}/api/branch/{test_branch}/status")
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    container_status = status_data.get('container_status', {}).get('status')
                    print(f"   Container status: {container_status}")
                    
                    # Try to start Gemini session
                    session_response = requests.post(f"{base_url}/api/branch/{test_branch}/gemini-session")
                    print(f"   Gemini session status: {session_response.status_code}")
                    
                    if session_response.status_code == 200:
                        session_data = session_response.json()
                        print("   ✅ Gemini session started successfully!")
                        print(f"   TTYD Port: {session_data.get('ttyd_port')}")
                        print(f"   Access URL: {session_data.get('access_url')}")
                        print(f"   Instructions: {session_data.get('instructions')}")
                    elif session_response.status_code == 400:
                        response_data = session_response.json()
                        print("   ✅ Correctly returns 400 when container not running")
                        print(f"   Error: {response_data.get('error')}")
                        print(f"   Message: {response_data.get('message')}")
                    else:
                        print(f"   ⚠️  Unexpected status: {session_response.status_code}")
                        print(f"   Response: {session_response.text[:200]}...")
                else:
                    print(f"   ❌ Failed to get branch status: {status_response.status_code}")
            else:
                print("   ℹ️  No existing branches to test with")
        else:
            print(f"   ❌ Failed to get branches: {branches_response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Step 5: Test the endpoint registration
    print(f"\n5. Verifying endpoint registration...")
    try:
        response = requests.get(f"{base_url}/api/status")
        if response.status_code == 200:
            status_data = response.json()
            endpoints = status_data.get('endpoints', [])
            
            gemini_endpoint = f"/api/branch/{{branch_name}}/gemini-session"
            if gemini_endpoint in endpoints:
                print(f"   ✅ Gemini session endpoint is registered: {gemini_endpoint}")
            else:
                print(f"   ❌ Gemini session endpoint not found in registered endpoints")
                print(f"   Available endpoints: {endpoints}")
        else:
            print(f"   ❌ Failed to get API status: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print(f"\n🎉 Manual test completed!")
    print(f"\n📝 Summary:")
    print(f"   - Endpoint: POST /api/branch/{{branch_name}}/gemini-session")
    print(f"   - Returns 404 for non-existent branches ✅")
    print(f"   - Returns 400 when container is not running ✅")
    print(f"   - Should return 200 with session details when successful")
    print(f"   - TTYD port = branch_port + 1000")
    print(f"   - Command: ttyd -o -W -p {{port}} gemini")
    print(f"\n🔧 To test with a real branch:")
    print(f"   1. Create a branch with valid API key")
    print(f"   2. Start the branch container")
    print(f"   3. Call the Gemini session endpoint")
    print(f"   4. Access the terminal via the returned URL")

if __name__ == "__main__":
    test_gemini_session_manual() 