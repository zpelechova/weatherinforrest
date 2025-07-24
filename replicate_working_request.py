#!/usr/bin/env python3
"""
Replicate the exact working cURL request from API Explorer
"""

import hashlib
import hmac
import time
import requests
import os

def test_exact_working_request():
    """Test using the exact headers and values from working cURL"""
    
    # Extract exact values from working cURL
    access_id = "fxtdf9uy9uef3qv9nege"
    access_token = "6d55cbfe06ab95b58570194eac966174"  # From your working cURL
    timestamp = "1753354989898"  # From your working cURL
    working_signature = "592D94BDE156271A32D9AC2562AB789BAA1E6801D0C2790AFFE0F8FFA208950C"
    
    print("=== REPLICATING EXACT WORKING REQUEST ===")
    print(f"Using exact values from your working cURL:")
    print(f"Timestamp: {timestamp}")
    print(f"Signature: {working_signature}")
    
    # The exact working URL
    url = "https://openapi.tuyaeu.com/v2.0/cloud/thing/bf5f5736feb7d67046gdkw/firmware"
    
    headers = {
        'sign_method': 'HMAC-SHA256',
        'client_id': access_id,
        't': timestamp,
        'mode': 'cors',
        'Content-Type': 'application/json',
        'sign': working_signature,
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        result = response.json()
        
        print(f"Response: {result}")
        
        if result.get('success'):
            print("✅ Exact replication works!")
            return True
        else:
            print(f"❌ Replication failed: {result}")
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
    
    return False

def reverse_engineer_signature():
    """Try to reverse engineer how the signature was generated"""
    
    access_id = "fxtdf9uy9uef3qv9nege"
    access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
    access_token = "6d55cbfe06ab95b58570194eac966174"
    timestamp = "1753354989898"
    expected_signature = "592D94BDE156271A32D9AC2562AB789BAA1E6801D0C2790AFFE0F8FFA208950C"
    
    url = "https://openapi.tuyaeu.com/v2.0/cloud/thing/bf5f5736feb7d67046gdkw/firmware"
    method = "GET"
    
    print("\n=== REVERSE ENGINEERING SIGNATURE ===")
    
    # Method 1: Standard format with access_token
    content_hash = hashlib.sha256(''.encode()).hexdigest()
    string_to_sign = f"{method}\n{content_hash}\n\n{url}"
    signature_input1 = f"{access_id}{access_token}{timestamp}{string_to_sign}"
    signature1 = hmac.new(access_key.encode(), signature_input1.encode(), hashlib.sha256).hexdigest().upper()
    
    print(f"Method 1 - With access_token: {signature1}")
    print(f"Expected:                     {expected_signature}")
    print(f"Match: {signature1 == expected_signature}")
    
    # Method 2: Different string format
    string_to_sign2 = f"{method}\n{content_hash}\n\n/v2.0/cloud/thing/bf5f5736feb7d67046gdkw/firmware"
    signature_input2 = f"{access_id}{access_token}{timestamp}{string_to_sign2}"
    signature2 = hmac.new(access_key.encode(), signature_input2.encode(), hashlib.sha256).hexdigest().upper()
    
    print(f"Method 2 - Path only:         {signature2}")
    print(f"Match: {signature2 == expected_signature}")
    
    # Method 3: Without query parameters (firmware endpoint)
    # Try different combinations
    variations = [
        f"{access_id}{access_token}{timestamp}GET\n{content_hash}\n\n{url}",
        f"{access_id}{access_token}{timestamp}GET\n{content_hash}\n\n/v2.0/cloud/thing/bf5f5736feb7d67046gdkw/firmware",
        f"{access_id}{timestamp}{access_token}GET\n{content_hash}\n\n{url}",
        f"{access_id}{timestamp}GET\n{content_hash}\n\n{url}",
    ]
    
    for i, variation in enumerate(variations, 3):
        sig = hmac.new(access_key.encode(), variation.encode(), hashlib.sha256).hexdigest().upper()
        print(f"Method {i}: {sig}")
        print(f"Match: {sig == expected_signature}")

if __name__ == "__main__":
    # First test the exact working request
    working = test_exact_working_request()
    
    # Then try to reverse engineer the signature
    reverse_engineer_signature()