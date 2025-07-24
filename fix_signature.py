#!/usr/bin/env python3
"""
Fix signature generation based on working API Explorer method
"""

import hashlib
import hmac
import time
import json
import requests
import os

def create_correct_signature(method, url, body, access_id, access_key, timestamp, nonce=""):
    """Create signature using the exact method that works in API Explorer"""
    
    # Handle body - empty string for GET requests
    if body is None or (isinstance(body, dict) and not body):
        body_str = ""
    else:
        body_str = json.dumps(body, separators=(',', ':'))
    
    # Content hash
    content_hash = hashlib.sha256(body_str.encode()).hexdigest()
    
    # Headers to sign (empty for basic requests)
    headers_to_sign = ""
    
    # String to sign format that works with API Explorer
    string_to_sign = f"{method}\n{content_hash}\n{headers_to_sign}\n{url}"
    
    # Full signature string - this is the key part that was wrong
    signature_input = f"{access_id}{timestamp}{nonce}{string_to_sign}"
    
    # Create HMAC-SHA256 signature
    signature = hmac.new(
        access_key.encode(),
        signature_input.encode(),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature

def test_corrected_api_call():
    """Test with the corrected signature method"""
    
    access_id = os.getenv('NEW_TUYA_ACCESS_ID')
    access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
    device_id = os.getenv('NEW_TUYA_DEVICE_ID')
    
    print("=== TESTING CORRECTED SIGNATURE ===")
    print(f"Access ID: {access_id[:8]}...")
    print(f"Device ID: {device_id}")
    
    # Test token request first
    timestamp = int(time.time() * 1000)
    token_url = "https://openapi.tuyaeu.com/v1.0/token?grant_type=1"
    
    signature = create_correct_signature(
        "GET", token_url, None, access_id, access_key, timestamp
    )
    
    headers = {
        'client_id': access_id,
        't': str(timestamp),
        'sign_method': 'HMAC-SHA256',
        'sign': signature,
        'Content-Type': 'application/json'
    }
    
    print("Testing token request...")
    try:
        response = requests.get(token_url, headers=headers, timeout=10)
        result = response.json()
        
        if result.get('success'):
            token = result['result']['access_token']
            print(f"✅ Token obtained: {token[:20]}...")
            
            # Now test device data request
            print("Testing device data request...")
            device_url = f"https://openapi.tuyaeu.com/v1.0/devices/{device_id}"
            timestamp2 = int(time.time() * 1000)
            
            device_signature = create_correct_signature(
                "GET", device_url, None, access_id, access_key, timestamp2
            )
            
            device_headers = {
                'client_id': access_id,
                'access_token': token,
                't': str(timestamp2),
                'sign_method': 'HMAC-SHA256', 
                'sign': device_signature,
                'Content-Type': 'application/json'
            }
            
            device_response = requests.get(device_url, headers=device_headers, timeout=10)
            device_result = device_response.json()
            
            if device_result.get('success'):
                print("✅ Device data retrieved successfully!")
                print("Device info:")
                device_info = device_result['result']
                print(f"  Name: {device_info.get('name', 'Unknown')}")
                print(f"  Online: {device_info.get('online', 'Unknown')}")
                print(f"  Status: {device_info.get('status', [])}")
                return True
            else:
                print(f"❌ Device request failed: {device_result}")
                
        else:
            print(f"❌ Token request failed: {result}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        import traceback
        traceback.print_exc()
    
    return False

if __name__ == "__main__":
    success = test_corrected_api_call()
    if success:
        print("\n✅ SUCCESS! Signature method is now working.")
        print("Next: Update tuya_client.py with the corrected signature method.")
    else:
        print("\n❌ Still having issues. The API Explorer method may be different.")
        print("Please check what exact parameters the API Explorer is sending.")