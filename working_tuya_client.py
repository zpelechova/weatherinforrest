#!/usr/bin/env python3
"""
Working Tuya client based on successful API Explorer request
"""

import hashlib
import hmac
import time
import json
import requests
import os
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class WorkingTuyaClient:
    def __init__(self):
        self.access_id = os.getenv('NEW_TUYA_ACCESS_ID')
        self.access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
        self.token = None
        self.token_expires = None
        self.api_endpoint = "https://openapi.tuyaeu.com"  # Based on working request
        
    def _create_signature(self, method, url, body, timestamp, access_token=None):
        """Create signature using the exact method from working API Explorer"""
        
        # Content hash - empty for GET requests
        if body:
            content_hash = hashlib.sha256(json.dumps(body, separators=(',', ':')).encode()).hexdigest()
        else:
            content_hash = hashlib.sha256(''.encode()).hexdigest()
        
        # String to sign format from working request
        string_to_sign = f"{method}\n{content_hash}\n\n{url}"
        
        # Signature string - include access_token if available (for device requests)
        if access_token:
            signature_input = f"{self.access_id}{access_token}{timestamp}{string_to_sign}"
        else:
            signature_input = f"{self.access_id}{timestamp}{string_to_sign}"
        
        # Create HMAC-SHA256 signature
        signature = hmac.new(
            self.access_key.encode(),
            signature_input.encode(),
            hashlib.sha256
        ).hexdigest().upper()
        
        return signature
    
    def get_token(self):
        """Get access token using working signature method"""
        if (self.token and self.token_expires and 
            datetime.now() < self.token_expires):
            return self.token
            
        timestamp = int(time.time() * 1000)
        url = f"{self.api_endpoint}/v1.0/token?grant_type=1"
        
        signature = self._create_signature("GET", url, None, timestamp)
        
        headers = {
            'client_id': self.access_id,
            't': str(timestamp),
            'sign_method': 'HMAC-SHA256',
            'sign': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                self.token = result['result']['access_token']
                expire_time = result['result'].get('expire_time', 7200)
                self.token_expires = datetime.now() + timedelta(seconds=expire_time - 60)
                logger.info("Successfully obtained access token")
                return self.token
            else:
                logger.error(f"Token request failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Token request exception: {e}")
            return None
    
    def get_device_data(self):
        """Get device data using the working v2.0 endpoint"""
        token = self.get_token()
        if not token:
            return None
            
        # Use v2.0 endpoint like the working API Explorer request
        timestamp = int(time.time() * 1000)
        url = f"{self.api_endpoint}/v2.0/cloud/thing/{self.device_id}"
        
        signature = self._create_signature("GET", url, None, timestamp, token)
        
        headers = {
            'client_id': self.access_id,
            'access_token': token,
            't': str(timestamp),
            'sign_method': 'HMAC-SHA256',
            'sign': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                logger.info("Successfully retrieved device data")
                return result['result']
            else:
                logger.error(f"Device request failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Device request exception: {e}")
            return None
    
    def test_connection(self):
        """Test the connection using working method"""
        print("=== TESTING WORKING TUYA CLIENT ===")
        print(f"Access ID: {self.access_id[:8]}...")
        print(f"Device ID: {self.device_id}")
        
        # Test token
        print("1. Getting access token...")
        token = self.get_token()
        if token:
            print(f"✅ Token obtained: {token[:20]}...")
        else:
            print("❌ Failed to get token")
            return False
            
        # Test device data
        print("2. Getting device data...")
        device_data = self.get_device_data()
        if device_data:
            print("✅ Device data retrieved!")
            print(f"Device info: {device_data}")
            return True
        else:
            print("❌ Failed to get device data")
            return False

if __name__ == "__main__":
    client = WorkingTuyaClient()
    success = client.test_connection()
    
    if success:
        print("\n🎉 SUCCESS! The API connection is now working!")
        print("Next step: Update the main tuya_client.py with this working method")
    else:
        print("\n❌ Still having issues. Need to debug further.")