"""Test GARNI 925T connection with fresh Tuya credentials."""

import requests
import json
import hashlib
import hmac
import time
import os
from datetime import datetime

# Use the new credentials
TUYA_ACCESS_ID = os.getenv('NEW_TUYA_ACCESS_ID')
TUYA_ACCESS_KEY = os.getenv('NEW_TUYA_ACCESS_KEY') 
TUYA_DEVICE_ID = os.getenv('NEW_TUYA_DEVICE_ID')

def test_fresh_credentials():
    """Test connection with the fresh credentials."""
    print("=== Testing Fresh GARNI 925T Credentials ===\n")
    
    # Validate new credentials
    print("Step 1: Validating fresh credentials...")
    if not TUYA_ACCESS_ID or len(TUYA_ACCESS_ID) != 20:
        print(f"❌ NEW_ACCESS_ID invalid: {len(TUYA_ACCESS_ID) if TUYA_ACCESS_ID else 0} chars")
        return False
    
    if not TUYA_ACCESS_KEY or len(TUYA_ACCESS_KEY) != 32:
        print(f"❌ NEW_ACCESS_KEY invalid: {len(TUYA_ACCESS_KEY) if TUYA_ACCESS_KEY else 0} chars")
        return False
    
    print(f"✅ Fresh credentials format valid")
    print(f"   NEW_ACCESS_ID: {TUYA_ACCESS_ID[:8]}... ({'DIFFERENT' if not TUYA_ACCESS_ID.startswith('a35gfn8k') else 'SAME AS OLD'})")
    print(f"   DEVICE_ID: {TUYA_DEVICE_ID}")
    
    # Test token request with new credentials
    print("\nStep 2: Testing token request with fresh credentials...")
    
    endpoints = [
        ("EU", "https://openapi.tuyaeu.com"),
        ("US", "https://openapi.tuyaus.com"),
        ("CN", "https://openapi.tuyacn.com")
    ]
    
    for region, endpoint in endpoints:
        print(f"\n--- Testing {region} endpoint ---")
        success = test_token_request_new(endpoint)
        if success:
            print(f"🎉 SUCCESS! {region} endpoint works with fresh credentials!")
            
            # Test device data retrieval
            print("\nStep 3: Testing device data retrieval...")
            weather_data = test_device_data(endpoint)
            if weather_data:
                print("🎉 SUCCESS! Weather data retrieved from GARNI 925T!")
                print("Weather data:", json.dumps(weather_data, indent=2))
                return True
            else:
                print("⚠️ Connected but no weather data available")
                return True  # Connection works, data might be device-specific
        
    print("\n❌ All endpoints failed with fresh credentials")
    return False

def test_token_request_new(endpoint):
    """Test token request with new credentials."""
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        url_path = "/v1.0/token"
        body = ""
        
        # Create signature with new credentials
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        
        headers_for_sign = [
            f"client_id:{TUYA_ACCESS_ID}",
            f"sign_method:HMAC-SHA256", 
            f"t:{timestamp}"
        ]
        headers_str = "\n".join(headers_for_sign)
        
        string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{url_path}"
        
        signature = hmac.new(
            TUYA_ACCESS_KEY.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{endpoint}{url_path}", headers=headers, timeout=10)
        response_data = response.json()
        
        if response_data.get("success"):
            print(f"✅ Token retrieved: {response_data.get('result', {}).get('access_token', 'N/A')[:20]}...")
            return response_data.get('result', {}).get('access_token')
        else:
            print(f"❌ Token request failed: {response_data.get('msg', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def test_device_data(endpoint):
    """Test retrieving device data."""
    try:
        # First get token
        token = test_token_request_new(endpoint)
        if not token:
            return None
        
        # Get device status
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        url_path = f"/v1.0/devices/{TUYA_DEVICE_ID}/status"
        body = ""
        
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        
        headers_for_sign = [
            f"access_token:{token}",
            f"client_id:{TUYA_ACCESS_ID}",
            f"sign_method:HMAC-SHA256",
            f"t:{timestamp}"
        ]
        headers_str = "\n".join(headers_for_sign)
        
        string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{url_path}"
        
        signature = hmac.new(
            TUYA_ACCESS_KEY.encode(),
            string_to_sign.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        headers = {
            "access_token": token,
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256", 
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{endpoint}{url_path}", headers=headers, timeout=10)
        response_data = response.json()
        
        if response_data.get("success"):
            return response_data.get("result", [])
        else:
            print(f"Device request failed: {response_data.get('msg', 'Unknown error')}")
            return None
            
    except Exception as e:
        print(f"Device data request failed: {e}")
        return None

if __name__ == "__main__":
    test_fresh_credentials()