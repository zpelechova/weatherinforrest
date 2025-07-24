"""Diagnostic tool for Tuya API connection issues."""

import requests
import json
import hashlib
import hmac
import time
from config import TUYA_ACCESS_ID, TUYA_ACCESS_KEY, TUYA_DEVICE_ID

def test_tuya_endpoints():
    """Test connection to different Tuya regional endpoints."""
    endpoints = [
        "https://openapi.tuyaeu.com",
        "https://openapi.tuyaus.com", 
        "https://openapi.tuyacn.com"
    ]
    
    print("Testing Tuya regional endpoints...")
    
    for endpoint in endpoints:
        try:
            response = requests.get(f"{endpoint}/v1.0/token", timeout=5)
            print(f"{endpoint}: Status {response.status_code}")
            if response.status_code == 405:
                print(f"  ✓ Endpoint reachable (expects POST)")
            elif response.status_code == 200:
                print(f"  ✓ Endpoint accessible")
            else:
                print(f"  ⚠ Unexpected response: {response.text[:100]}")
        except Exception as e:
            print(f"{endpoint}: ✗ Connection failed - {e}")

def test_credential_format():
    """Validate credential format."""
    print("\nValidating credential format...")
    
    if not TUYA_ACCESS_ID:
        print("✗ TUYA_ACCESS_ID missing")
        return False
    
    if len(TUYA_ACCESS_ID) != 20:
        print(f"✗ ACCESS_ID length incorrect: {len(TUYA_ACCESS_ID)} (should be 20)")
        return False
    
    if not TUYA_ACCESS_KEY:
        print("✗ TUYA_ACCESS_KEY missing")
        return False
        
    if len(TUYA_ACCESS_KEY) != 32:
        print(f"✗ ACCESS_KEY length incorrect: {len(TUYA_ACCESS_KEY)} (should be 32)")
        return False
    
    if not TUYA_DEVICE_ID:
        print("✗ TUYA_DEVICE_ID missing")
        return False
        
    if len(TUYA_DEVICE_ID) != 22:
        print(f"✗ DEVICE_ID length incorrect: {len(TUYA_DEVICE_ID)} (should be 22)")
        return False
    
    print("✓ All credentials have correct format")
    return True

def test_signature_generation():
    """Test signature generation method."""
    print("\nTesting signature generation...")
    
    timestamp = str(int(time.time() * 1000))
    method = "GET"
    url = "/v1.0/token"
    
    # Test signature creation
    try:
        content_hash = hashlib.sha256("".encode()).hexdigest()
        headers_str = f"client_id:{TUYA_ACCESS_ID}\nsign_method:HMAC-SHA256\nt:{timestamp}"
        string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{url}"
        
        signature = hmac.new(
            TUYA_ACCESS_KEY.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        print(f"✓ Signature generated successfully")
        print(f"  String to sign: {string_to_sign[:50]}...")
        print(f"  Signature: {signature[:16]}...")
        
        return True
    except Exception as e:
        print(f"✗ Signature generation failed: {e}")
        return False

if __name__ == "__main__":
    test_tuya_endpoints()
    test_credential_format() 
    test_signature_generation()