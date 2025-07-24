"""Comprehensive Tuya API diagnostics for GARNI 925T connection."""

import requests
import json
import hashlib
import hmac
import time
import os
from urllib.parse import quote

# Use fresh credentials
TUYA_ACCESS_ID = os.getenv('NEW_TUYA_ACCESS_ID')
TUYA_ACCESS_KEY = os.getenv('NEW_TUYA_ACCESS_KEY')
TUYA_DEVICE_ID = os.getenv('NEW_TUYA_DEVICE_ID')

def comprehensive_tuya_test():
    """Run comprehensive Tuya API diagnostics."""
    print("=== Comprehensive GARNI 925T API Diagnostics ===\n")
    
    # Test 1: Different signature methods
    print("Test 1: Trying different signature generation methods...")
    test_signature_variations()
    
    # Test 2: Different header formats
    print("\nTest 2: Trying different header formats...")
    test_header_variations()
    
    # Test 3: Different endpoints and paths
    print("\nTest 3: Trying different API endpoints...")
    test_endpoint_variations()
    
    # Test 4: Timestamp variations
    print("\nTest 4: Testing timestamp handling...")
    test_timestamp_variations()

def test_signature_variations():
    """Test different signature generation methods."""
    endpoint = "https://openapi.tuyaeu.com"
    timestamp = str(int(time.time() * 1000))
    
    variations = [
        ("Standard HMAC-SHA256", generate_signature_standard),
        ("Alternative ordering", generate_signature_alt_order),
        ("URL encoded", generate_signature_url_encoded),
        ("Different hash method", generate_signature_different_hash)
    ]
    
    for name, sig_func in variations:
        print(f"  Testing {name}...")
        success = test_with_signature_method(endpoint, timestamp, sig_func)
        if success:
            print(f"    ✅ {name} worked!")
            return True
        else:
            print(f"    ❌ {name} failed")
    
    return False

def test_header_variations():
    """Test different header format variations."""
    endpoint = "https://openapi.tuyaeu.com"
    timestamp = str(int(time.time() * 1000))
    
    # Test with different header combinations
    header_sets = [
        {
            "client_id": TUYA_ACCESS_ID,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        },
        {
            "client_id": TUYA_ACCESS_ID,
            "sign_method": "HMAC-SHA256", 
            "t": timestamp,
            "Content-Type": "application/x-www-form-urlencoded"
        },
        {
            "client_id": TUYA_ACCESS_ID,
            "sign_method": "HMAC-SHA256",
            "t": timestamp
        }
    ]
    
    for i, base_headers in enumerate(header_sets):
        print(f"  Testing header set {i+1}...")
        signature = generate_signature_standard(timestamp, base_headers)
        headers = {**base_headers, "sign": signature}
        
        success = make_test_request(endpoint, headers)
        if success:
            print(f"    ✅ Header set {i+1} worked!")
            return True
        else:
            print(f"    ❌ Header set {i+1} failed")
    
    return False

def test_endpoint_variations():
    """Test different API endpoints and paths."""
    endpoints = [
        ("EU Main", "https://openapi.tuyaeu.com"),
        ("EU Alt", "https://openapi-ueaz.tuyaeu.com"),
        ("US Main", "https://openapi.tuyaus.com"),
        ("US West", "https://openapi-weaz.tuyaus.com"),
        ("China", "https://openapi.tuyacn.com")
    ]
    
    timestamp = str(int(time.time() * 1000))
    
    for name, endpoint in endpoints:
        print(f"  Testing {name}: {endpoint}")
        success = test_basic_connection(endpoint, timestamp)
        if success:
            print(f"    ✅ {name} responded successfully!")
            return endpoint
        else:
            print(f"    ❌ {name} failed")
    
    return None

def test_timestamp_variations():
    """Test different timestamp formats."""
    endpoint = "https://openapi.tuyaeu.com"
    
    # Test different timestamp formats
    current_time = time.time()
    timestamps = [
        str(int(current_time * 1000)),  # Milliseconds
        str(int(current_time)),         # Seconds
        str(int((current_time - 60) * 1000)),  # 1 minute ago
        str(int((current_time + 60) * 1000))   # 1 minute future
    ]
    
    for i, timestamp in enumerate(timestamps):
        print(f"  Testing timestamp format {i+1}: {timestamp}")
        success = test_basic_connection(endpoint, timestamp)
        if success:
            print(f"    ✅ Timestamp format {i+1} worked!")
            return True
        else:
            print(f"    ❌ Timestamp format {i+1} failed")
    
    return False

def generate_signature_standard(timestamp, headers=None):
    """Standard signature generation."""
    method = "GET"
    url_path = "/v1.0/token"
    body = ""
    
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
    
    return signature

def generate_signature_alt_order(timestamp, headers=None):
    """Alternative header ordering."""
    method = "GET"
    url_path = "/v1.0/token"
    body = ""
    
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    
    # Different order
    headers_for_sign = [
        f"sign_method:HMAC-SHA256",
        f"client_id:{TUYA_ACCESS_ID}",
        f"t:{timestamp}"
    ]
    headers_str = "\n".join(headers_for_sign)
    
    string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{url_path}"
    
    signature = hmac.new(
        TUYA_ACCESS_KEY.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature

def generate_signature_url_encoded(timestamp, headers=None):
    """URL encoded signature."""
    method = "GET"
    url_path = "/v1.0/token"
    body = ""
    
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    
    headers_for_sign = [
        f"client_id:{quote(TUYA_ACCESS_ID)}",
        f"sign_method:HMAC-SHA256",
        f"t:{timestamp}"
    ]
    headers_str = "\n".join(headers_for_sign)
    
    string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{quote(url_path)}"
    
    signature = hmac.new(
        TUYA_ACCESS_KEY.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest().upper()
    
    return signature

def generate_signature_different_hash(timestamp, headers=None):
    """Different hash method."""
    method = "GET"
    url_path = "/v1.0/token"
    body = ""
    
    content_hash = hashlib.sha256(body.encode()).hexdigest()
    
    headers_for_sign = [
        f"client_id:{TUYA_ACCESS_ID}",
        f"sign_method:HMAC-SHA256",
        f"t:{timestamp}"
    ]
    headers_str = "\n".join(headers_for_sign)
    
    string_to_sign = f"{method}\n{content_hash}\n{headers_str}\n{url_path}"
    
    # Try lowercase
    signature = hmac.new(
        TUYA_ACCESS_KEY.encode(),
        string_to_sign.encode(),
        hashlib.sha256
    ).hexdigest()  # No .upper()
    
    return signature

def test_with_signature_method(endpoint, timestamp, sig_func):
    """Test API call with specific signature method."""
    try:
        signature = sig_func(timestamp)
        
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        return make_test_request(endpoint, headers)
        
    except Exception as e:
        return False

def test_basic_connection(endpoint, timestamp):
    """Test basic connection to endpoint."""
    try:
        signature = generate_signature_standard(timestamp)
        
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        return make_test_request(endpoint, headers)
        
    except Exception as e:
        return False

def make_test_request(endpoint, headers):
    """Make test request to API."""
    try:
        response = requests.get(f"{endpoint}/v1.0/token", headers=headers, timeout=10)
        response_data = response.json()
        
        success = response_data.get("success", False)
        if success:
            print(f"      Response: SUCCESS - Token received")
        else:
            error_msg = response_data.get("msg", "Unknown error")
            error_code = response_data.get("code", "Unknown")
            print(f"      Response: FAIL - {error_code}: {error_msg}")
        
        return success
        
    except Exception as e:
        print(f"      Response: ERROR - {e}")
        return False

if __name__ == "__main__":
    comprehensive_tuya_test()