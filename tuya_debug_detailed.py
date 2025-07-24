"""Detailed Tuya connection troubleshooting and testing."""

import requests
import json
import hashlib
import hmac
import time
import os
from datetime import datetime
from config import TUYA_ACCESS_ID, TUYA_ACCESS_KEY, TUYA_DEVICE_ID

def test_step_by_step():
    """Test Tuya connection step by step."""
    print("=== GARNI 925T Tuya Connection Diagnosis ===\n")
    
    # Step 1: Credential validation
    print("Step 1: Validating credentials...")
    if not TUYA_ACCESS_ID or len(TUYA_ACCESS_ID) != 20:
        print(f"❌ ACCESS_ID invalid: {len(TUYA_ACCESS_ID) if TUYA_ACCESS_ID else 0} chars")
        return False
    
    if not TUYA_ACCESS_KEY or len(TUYA_ACCESS_KEY) != 32:
        print(f"❌ ACCESS_KEY invalid: {len(TUYA_ACCESS_KEY) if TUYA_ACCESS_KEY else 0} chars")
        return False
        
    if not TUYA_DEVICE_ID or len(TUYA_DEVICE_ID) != 22:
        print(f"❌ DEVICE_ID invalid: {len(TUYA_DEVICE_ID) if TUYA_DEVICE_ID else 0} chars")
        return False
    
    print(f"✅ Credentials format valid")
    print(f"   ACCESS_ID: {TUYA_ACCESS_ID[:8]}...")
    print(f"   DEVICE_ID: {TUYA_DEVICE_ID}")
    
    # Step 2: Test endpoints
    print("\nStep 2: Testing regional endpoints...")
    endpoints = {
        "EU": "https://openapi.tuyaeu.com",
        "US": "https://openapi.tuyaus.com",
        "CN": "https://openapi.tuyacn.com"
    }
    
    for region, endpoint in endpoints.items():
        try:
            response = requests.get(f"{endpoint}/v1.0/token", timeout=5)
            print(f"   {region}: {response.status_code} - {'✅' if response.status_code in [200, 405] else '❌'}")
        except Exception as e:
            print(f"   {region}: ❌ Connection failed - {e}")
    
    # Step 3: Test token request with detailed debugging
    print("\nStep 3: Testing token request with debug info...")
    
    for region, endpoint in endpoints.items():
        print(f"\n--- Testing {region} endpoint ---")
        success = test_token_request(endpoint)
        if success:
            print(f"✅ {region} endpoint working!")
            return True
        else:
            print(f"❌ {region} endpoint failed")
    
    return False

def test_token_request(endpoint):
    """Test token request with detailed debugging."""
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        url_path = "/v1.0/token"
        body = ""
        
        print(f"Endpoint: {endpoint}")
        print(f"Timestamp: {timestamp}")
        print(f"Method: {method}")
        print(f"Path: {url_path}")
        
        # Create signature
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        print(f"Content hash: {content_hash}")
        
        headers_for_sign = [
            f"client_id:{TUYA_ACCESS_ID}",
            f"sign_method:HMAC-SHA256",
            f"t:{timestamp}"
        ]
        headers_str = "\\n".join(headers_for_sign)
        print(f"Headers string: {headers_str}")
        
        string_to_sign = f"{method}\\n{content_hash}\\n{headers_str}\\n{url_path}"
        print(f"String to sign: {string_to_sign}")
        
        signature = hmac.new(
            TUYA_ACCESS_KEY.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        print(f"Generated signature: {signature}")
        
        # Prepare headers
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        print(f"Request headers: {headers}")
        
        # Make request
        full_url = f"{endpoint}{url_path}"
        print(f"Making request to: {full_url}")
        
        response = requests.get(full_url, headers=headers, timeout=10)
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        try:
            response_data = response.json()
            print(f"Response body: {json.dumps(response_data, indent=2)}")
            
            if response_data.get("success"):
                print("✅ Token request successful!")
                return True
            else:
                print(f"❌ Token request failed: {response_data.get('msg', 'Unknown error')}")
                if response_data.get('code') == 1004:
                    print("   This is a signature validation error")
                    print("   Possible causes:")
                    print("   - Wrong Access ID or Secret")
                    print("   - Device not linked to developer project")
                    print("   - Project region mismatch")
                    print("   - API permissions not enabled")
                return False
                
        except Exception as e:
            print(f"❌ Invalid JSON response: {e}")
            print(f"Raw response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def get_debug_info():
    """Get additional debug information."""
    print("\\n=== Debug Information ===")
    print(f"Current time: {datetime.now()}")
    print(f"Timestamp: {int(time.time() * 1000)}")
    print(f"Environment variables:")
    for key in ['TUYA_ACCESS_ID', 'TUYA_ACCESS_KEY', 'TUYA_DEVICE_ID']:
        value = os.getenv(key, '')
        print(f"  {key}: {'Set' if value else 'Not set'} ({len(value)} chars)")

if __name__ == "__main__":
    get_debug_info()
    test_step_by_step()