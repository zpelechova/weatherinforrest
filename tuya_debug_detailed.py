"""Detailed Tuya API debugging with version testing."""

import requests
import json
import hashlib
import hmac
import time
import os

# Use fresh credentials
TUYA_ACCESS_ID = os.getenv('NEW_TUYA_ACCESS_ID')
TUYA_ACCESS_KEY = os.getenv('NEW_TUYA_ACCESS_KEY')
TUYA_DEVICE_ID = os.getenv('NEW_TUYA_DEVICE_ID')

def detailed_debug():
    """Detailed debugging of Tuya API connection."""
    print("=== Detailed GARNI 925T API Debug ===\n")
    
    print("Credentials check:")
    print(f"Access ID: {TUYA_ACCESS_ID[:8]}... (length: {len(TUYA_ACCESS_ID)})")
    print(f"Access Key: {TUYA_ACCESS_KEY[:8]}... (length: {len(TUYA_ACCESS_KEY)})")
    print(f"Device ID: {TUYA_DEVICE_ID}")
    
    # Test different API versions
    print("\nTesting different API versions...")
    test_api_versions()
    
    # Test project info endpoint
    print("\nTesting project info endpoint...")
    test_project_info()
    
    # Test with minimal headers
    print("\nTesting with minimal headers...")
    test_minimal_headers()

def test_api_versions():
    """Test different API versions."""
    versions = [
        "/v1.0/token",
        "/v1.1/token", 
        "/v2.0/token",
        "/token"
    ]
    
    endpoint = "https://openapi.tuyaeu.com"
    
    for version in versions:
        print(f"  Testing version: {version}")
        success = test_version_endpoint(endpoint, version)
        if success:
            print(f"    ✅ Version {version} works!")
            return version
        else:
            print(f"    ❌ Version {version} failed")
    
    return None

def test_project_info():
    """Test project information endpoint."""
    # Some Tuya projects use different base URLs or require different setup
    endpoints = [
        "https://openapi.tuyaeu.com/v1.0/iot-03/app-info",
        "https://openapi.tuyaeu.com/v1.0/users/me",
        "https://openapi.tuyaeu.com/v1.0/devices",
        "https://openapi.tuyaus.com/v1.0/iot-03/app-info"
    ]
    
    for endpoint_path in endpoints:
        print(f"  Testing: {endpoint_path}")
        success = test_endpoint_directly(endpoint_path)
        if success:
            print(f"    ✅ Endpoint responds!")
            return True
        else:
            print(f"    ❌ Endpoint failed")
    
    return False

def test_minimal_headers():
    """Test with absolutely minimal headers."""
    timestamp = str(int(time.time() * 1000))
    endpoint = "https://openapi.tuyaeu.com"
    
    # Ultra minimal signature
    method = "GET"
    url_path = "/v1.0/token"
    body = ""
    
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    
    # Test different signature string formats
    signature_formats = [
        # Format 1: Standard
        f"GET\n{content_hash}\nclient_id:{TUYA_ACCESS_ID}\nsign_method:HMAC-SHA256\nt:{timestamp}\n/v1.0/token",
        
        # Format 2: Without newlines at end
        f"GET\n{content_hash}\nclient_id:{TUYA_ACCESS_ID}\nsign_method:HMAC-SHA256\nt:{timestamp}\n/v1.0/token",
        
        # Format 3: Different ordering
        f"GET\n{content_hash}\nt:{timestamp}\nclient_id:{TUYA_ACCESS_ID}\nsign_method:HMAC-SHA256\n/v1.0/token",
        
        # Format 4: Simple format
        f"{TUYA_ACCESS_ID}{timestamp}/v1.0/token",
    ]
    
    for i, sig_string in enumerate(signature_formats):
        print(f"  Testing signature format {i+1}...")
        
        signature = hmac.new(
            TUYA_ACCESS_KEY.encode(),
            sig_string.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp
        }
        
        success = make_request(endpoint + url_path, headers)
        if success:
            print(f"    ✅ Format {i+1} works!")
            return True
        else:
            print(f"    ❌ Format {i+1} failed")
    
    return False

def test_version_endpoint(endpoint, version_path):
    """Test specific API version endpoint."""
    try:
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        body = ""
        
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        
        headers_for_sign = [
            f"client_id:{TUYA_ACCESS_ID}",
            f"sign_method:HMAC-SHA256",
            f"t:{timestamp}"
        ]
        headers_str = "\n".join(headers_for_sign)
        
        string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{version_path}"
        
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
        
        return make_request(endpoint + version_path, headers)
        
    except Exception as e:
        return False

def test_endpoint_directly(full_endpoint):
    """Test endpoint directly without token."""
    try:
        timestamp = str(int(time.time() * 1000))
        
        # Extract path from full URL
        if "://" in full_endpoint:
            base_url = "/".join(full_endpoint.split("/")[:3])
            path = "/" + "/".join(full_endpoint.split("/")[3:])
        else:
            return False
        
        method = "GET"
        body = ""
        
        content_hash = hashlib.sha256(body.encode()).hexdigest()
        
        headers_for_sign = [
            f"client_id:{TUYA_ACCESS_ID}",
            f"sign_method:HMAC-SHA256",
            f"t:{timestamp}"
        ]
        headers_str = "\n".join(headers_for_sign)
        
        string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{path}"
        
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
        
        return make_request(full_endpoint, headers)
        
    except Exception as e:
        return False

def make_request(url, headers):
    """Make request and return success status."""
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response_data = response.json()
        
        success = response_data.get("success", False)
        if success:
            print(f"        SUCCESS: {response_data.get('result', {})}")
        else:
            error_code = response_data.get("code", "Unknown")
            error_msg = response_data.get("msg", "Unknown error")
            print(f"        FAIL: {error_code} - {error_msg}")
        
        return success
        
    except Exception as e:
        print(f"        ERROR: {e}")
        return False

if __name__ == "__main__":
    detailed_debug()