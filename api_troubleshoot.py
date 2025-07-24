#!/usr/bin/env python3
"""
Advanced API troubleshooting for Tuya sign invalid error
"""

import hashlib
import hmac
import time
import json
import requests
import os

def create_enhanced_signature(method, url, body, access_key, secret_key, timestamp):
    """Create signature using exact Tuya specification"""
    
    # Content hash - SHA256 of body
    if body:
        content_hash = hashlib.sha256(json.dumps(body, separators=(',', ':')).encode()).hexdigest()
    else:
        content_hash = hashlib.sha256(''.encode()).hexdigest()
    
    # String to sign format: METHOD + "\n" + CONTENT-SHA256 + "\n" + "" + "\n" + URL
    string_to_sign = f"{method}\n{content_hash}\n\n{url}"
    
    # Full signature string: access_key + timestamp + string_to_sign
    signature_string = access_key + str(timestamp) + string_to_sign
    
    # HMAC-SHA256 signature
    signature = hmac.new(
        secret_key.encode(), 
        signature_string.encode(), 
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature, content_hash

def test_enhanced_token_request():
    """Test token request with enhanced signature method"""
    
    access_id = os.getenv('NEW_TUYA_ACCESS_ID')
    access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
    
    if not access_id or not access_key:
        print("❌ Missing credentials")
        return
    
    print("=== ENHANCED API TEST ===")
    print(f"Access ID: {access_id[:8]}...")
    
    endpoints = [
        "https://openapi.tuyaeu.com",
        "https://openapi.tuyaus.com", 
        "https://openapi.tuyacn.com"
    ]
    
    for base_url in endpoints:
        print(f"\nTesting: {base_url}")
        
        timestamp = int(time.time() * 1000)
        url = f"{base_url}/v1.0/token?grant_type=1"
        method = "GET"
        
        # Create signature using enhanced method
        signature, content_hash = create_enhanced_signature(
            method, url, None, access_id, access_key, timestamp
        )
        
        headers = {
            'client_id': access_id,
            't': str(timestamp),
            'sign_method': 'HMAC-SHA256',
            'sign': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                print(f"✅ SUCCESS: {base_url}")
                print(f"Token: {result['result']['access_token'][:20]}...")
                return result['result']['access_token'], base_url
            else:
                print(f"❌ Error: {result}")
                
                # Additional debugging info
                print(f"Signature string: {access_id}{timestamp}GET\\n{content_hash}\\n\\n{url}")
                print(f"Generated signature: {signature}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return None, None

def test_alternative_signature_methods():
    """Test different signature generation methods"""
    
    access_id = os.getenv('NEW_TUYA_ACCESS_ID')
    access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
    
    print("\n=== TESTING ALTERNATIVE SIGNATURE METHODS ===")
    
    timestamp = int(time.time() * 1000)
    url = "https://openapi.tuyaeu.com/v1.0/token?grant_type=1"
    method = "GET"
    
    # Method 1: Simple concatenation (sometimes works)
    simple_string = access_id + str(timestamp)
    simple_sig = hmac.new(access_key.encode(), simple_string.encode(), hashlib.sha256).hexdigest().upper()
    print(f"Method 1 - Simple: {simple_sig}")
    
    # Method 2: With empty body hash
    empty_hash = hashlib.sha256(''.encode()).hexdigest()
    method2_string = f"{access_id}{timestamp}{method}\n{empty_hash}\n\n{url}"
    method2_sig = hmac.new(access_key.encode(), method2_string.encode(), hashlib.sha256).hexdigest().upper()
    print(f"Method 2 - With body hash: {method2_sig}")
    
    # Method 3: Standard format
    string_to_sign = f"{method}\n{empty_hash}\n\n{url}"
    method3_string = f"{access_id}{timestamp}{string_to_sign}"
    method3_sig = hmac.new(access_key.encode(), method3_string.encode(), hashlib.sha256).hexdigest().upper()
    print(f"Method 3 - Standard: {method3_sig}")

if __name__ == "__main__":
    # Test enhanced signature
    token, endpoint = test_enhanced_token_request()
    
    # Test alternative methods for comparison
    test_alternative_signature_methods()
    
    if token:
        print(f"\n✅ SUCCESS! Working endpoint: {endpoint}")
        print("Next steps:")
        print("1. Update tuya_client.py to use working endpoint")
        print("2. Verify API service subscriptions in Tuya dashboard")
        print("3. Test device data retrieval")
    else:
        print("\n❌ All signature methods failed")
        print("Recommended actions:")
        print("1. Check API service subscriptions in Tuya IoT Platform")
        print("2. Verify app account linking")
        print("3. Confirm project was created after May 25, 2021")