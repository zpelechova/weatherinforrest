#!/usr/bin/env python3
"""
Fixed Tuya client with correct signature method
"""

import hashlib
import hmac
import time
import json
import requests
import os
from datetime import datetime, timedelta
import logging
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class TuyaWeatherClient:
    def __init__(self):
        self.access_id = os.getenv('NEW_TUYA_ACCESS_ID')
        self.access_key = os.getenv('NEW_TUYA_ACCESS_KEY')
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
        self.token = None
        self.token_expires = None
        self.api_endpoint = "https://openapi.tuyaeu.com"
        self.connection_status = "disconnected"
        self.last_error = None
        self.last_attempt = None
        
    def _create_signature(self, method, url, body, timestamp, access_token=None):
        """Create signature using the correct method - path only, not full URL"""
        
        # Parse URL to get path only
        parsed_url = urlparse(url)
        url_path = parsed_url.path
        if parsed_url.query:
            url_path += f"?{parsed_url.query}"
        
        # Content hash
        if body:
            content_hash = hashlib.sha256(json.dumps(body, separators=(',', ':')).encode()).hexdigest()
        else:
            content_hash = hashlib.sha256(''.encode()).hexdigest()
        
        # String to sign - use path only
        string_to_sign = f"{method}\n{content_hash}\n\n{url_path}"
        
        # Signature input - include access_token if available
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
    
    def _get_token(self):
        """Get access token with corrected signature"""
        if (self.token and self.token_expires and 
            datetime.now() < self.token_expires):
            return True
            
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
                self.connection_status = "connected"
                logger.info("Successfully obtained access token")
                return True
            else:
                logger.error(f"Token request failed: {result}")
                self.connection_status = "api_error"
                self.last_error = f"Token request failed: {result.get('msg', 'Unknown error')}"
                return False
                
        except Exception as e:
            logger.error(f"Token request exception: {e}")
            self.connection_status = "connection_error"
            self.last_error = str(e)
            return False
    
    def get_device_data(self):
        """Get device data using corrected signature and v2.0 endpoint"""
        if not self._get_token():
            return None
            
        timestamp = int(time.time() * 1000)
        # Use v2.0 endpoint for device data
        url = f"{self.api_endpoint}/v2.0/cloud/thing/{self.device_id}"
        
        signature = self._create_signature("GET", url, None, timestamp, self.token)
        
        headers = {
            'client_id': self.access_id,
            'access_token': self.token,
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
    
    def get_device_status(self):
        """Get device status/properties"""
        if not self._get_token():
            return None
            
        timestamp = int(time.time() * 1000)
        url = f"{self.api_endpoint}/v2.0/cloud/thing/{self.device_id}/shadow/properties"
        
        signature = self._create_signature("GET", url, None, timestamp, self.token)
        
        headers = {
            'client_id': self.access_id,
            'access_token': self.token,
            't': str(timestamp),
            'sign_method': 'HMAC-SHA256',
            'sign': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                return result['result']
            else:
                logger.error(f"Status request failed: {result}")
                return None
                
        except Exception as e:
            logger.error(f"Status request exception: {e}")
            return None
    
    def test_connection(self):
        """Test the connection"""
        self.last_attempt = datetime.now()
        
        if self._get_token():
            # Try to get device data
            device_data = self.get_device_data()
            if device_data:
                self.connection_status = "connected"
                logger.info("Tuya API connection test successful")
                return True
        
        self.connection_status = "api_error"
        logger.error("Tuya API connection test failed")
        return False
    
    def get_connection_status(self):
        """Get current connection status"""
        return {
            "status": self.connection_status,
            "last_error": self.last_error,
            "last_attempt": self.last_attempt
        }

def main():
    """Test the fixed client"""
    print("=== TESTING FIXED TUYA CLIENT ===")
    
    client = TuyaWeatherClient()
    
    print("1. Testing connection...")
    if client.test_connection():
        print("✅ Connection successful!")
        
        print("2. Getting device data...")
        device_data = client.get_device_data()
        if device_data:
            print(f"✅ Device data: {device_data}")
        
        print("3. Getting device status...")
        status_data = client.get_device_status()
        if status_data:
            print(f"✅ Status data: {status_data}")
            
        return True
    else:
        print("❌ Connection failed")
        status = client.get_connection_status()
        print(f"Status: {status}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SUCCESS! Ready to update the main weather monitoring system!")
    else:
        print("\n❌ Still debugging needed")