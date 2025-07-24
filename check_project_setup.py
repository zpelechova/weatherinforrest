"""Check if GARNI 925T is properly linked to the new Tuya project."""

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

def check_project_setup():
    """Check if the project setup is correct."""
    print("=== GARNI 925T Project Setup Diagnosis ===\n")
    
    print("Critical Setup Questions:")
    print("1. Is your GARNI 925T visible in the new project's Devices tab?")
    print("2. Did you link your Smart Life app account to this new project?")
    print("3. Are the required APIs enabled in this new project?")
    print("4. Is the project in the correct regional data center?")
    
    print(f"\nUsing credentials:")
    print(f"Access ID: {TUYA_ACCESS_ID[:8]}...")
    print(f"Device ID: {TUYA_DEVICE_ID}")
    
    # Try to get token for basic connection test
    endpoints = [
        ("EU", "https://openapi.tuyaeu.com"),
        ("US", "https://openapi.tuyaus.com"), 
        ("CN", "https://openapi.tuyacn.com")
    ]
    
    print("\nTesting basic connectivity...")
    for region, endpoint in endpoints:
        success = try_simple_token_request(endpoint)
        if success:
            print(f"✅ {region} endpoint accepts credentials")
            
            # Try to list devices if token works
            print(f"\nTrying to list devices in {region} project...")
            devices = list_project_devices(endpoint)
            if devices is not None:
                print(f"Devices found: {len(devices)}")
                for device in devices:
                    device_id = device.get('id', 'Unknown')
                    device_name = device.get('name', 'Unknown')
                    print(f"  - {device_name} (ID: {device_id})")
                    if device_id == TUYA_DEVICE_ID:
                        print(f"    ✅ GARNI 925T found in project!")
                        return True
                
                if not devices:
                    print("❌ No devices found in this project")
                    print("Your GARNI 925T is not linked to this project")
                else:
                    print(f"❌ GARNI 925T (ID: {TUYA_DEVICE_ID}) not found in project")
                    print("Device exists but isn't linked to this project")
            else:
                print("Could not retrieve device list")
        else:
            print(f"❌ {region} endpoint rejects credentials")
    
    print("\n=== Diagnosis ===")
    print("The 'sign invalid' error with fresh credentials indicates:")
    print("1. Device not linked to this project")
    print("2. Required APIs not enabled") 
    print("3. Project region mismatch")
    print("4. Smart Life account not linked to project")
    
    return False

def try_simple_token_request(endpoint):
    """Try basic token request."""
    try:
        timestamp = str(int(time.time() * 1000))
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
        
        headers = {
            "client_id": TUYA_ACCESS_ID,
            "sign": signature,
            "sign_method": "HMAC-SHA256",
            "t": timestamp,
            "Content-Type": "application/json"
        }
        
        response = requests.get(f"{endpoint}{url_path}", headers=headers, timeout=10)
        response_data = response.json()
        
        return response_data.get("success", False)
        
    except Exception as e:
        return False

def list_project_devices(endpoint):
    """Try to list devices in the project."""
    try:
        # First get token
        token = get_access_token(endpoint)
        if not token:
            return None
        
        # List devices
        timestamp = str(int(time.time() * 1000))
        method = "GET"
        url_path = "/v1.0/devices"
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
            return None
            
    except Exception as e:
        return None

def get_access_token(endpoint):
    """Get access token if credentials work."""
    try:
        timestamp = str(int(time.time() * 1000))
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
            return response_data.get("result", {}).get("access_token")
        else:
            return None
            
    except Exception as e:
        return None

if __name__ == "__main__":
    check_project_setup()