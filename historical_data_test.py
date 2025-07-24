#!/usr/bin/env python3
"""
Test historical data capabilities from GARNI 925T weather station
"""

import os
import requests
import hashlib
import hmac
import time
from datetime import datetime, timedelta
from urllib.parse import urlparse
from tuya_client import TuyaWeatherClient

def test_garni_historical_endpoints():
    """Test various Tuya API endpoints for historical data from GARNI 925T"""
    
    client = TuyaWeatherClient()
    if not client._get_token():
        print("❌ Failed to get access token")
        return
    
    device_id = os.getenv('NEW_TUYA_DEVICE_ID')
    print(f"=== TESTING GARNI 925T HISTORICAL DATA ===")
    print(f"Device ID: {device_id}")
    
    # Test different historical data endpoints
    historical_endpoints = [
        f"/v2.0/cloud/thing/{device_id}/shadow/properties/logs",  # Property logs
        f"/v1.0/devices/{device_id}/logs",  # Device logs
        f"/v1.0/devices/{device_id}/status",  # Current status
        f"/v2.0/cloud/thing/{device_id}/model",  # Device model info
        f"/v1.0/iot-03/devices/{device_id}/logs",  # IoT device logs
        f"/v1.0/devices/{device_id}/properties/logs",  # Properties logs
    ]
    
    for endpoint in historical_endpoints:
        print(f"\n📊 Testing: {endpoint}")
        
        # Add time range parameters for historical data
        end_time = int(time.time() * 1000)
        start_time = end_time - (24 * 60 * 60 * 1000)  # Last 24 hours
        
        # Try with time range parameters
        url_with_params = f"{client.api_endpoint}{endpoint}?start_time={start_time}&end_time={end_time}&limit=100"
        
        timestamp = int(time.time() * 1000)
        signature = client._create_signature("GET", url_with_params, None, timestamp, client.token)
        
        headers = {
            'client_id': client.access_id,
            'access_token': client.token,
            't': str(timestamp),
            'sign_method': 'HMAC-SHA256',
            'sign': signature,
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(url_with_params, headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                data = result.get('result', {})
                if isinstance(data, list):
                    print(f"   ✅ Found {len(data)} historical records")
                    if data:
                        # Show sample of historical data structure
                        print(f"   📋 Sample record: {str(data[0])[:200]}...")
                elif isinstance(data, dict):
                    print(f"   ✅ Found historical data structure")
                    print(f"   📋 Keys: {list(data.keys())}")
                else:
                    print(f"   ✅ Response received: {str(data)[:100]}...")
            else:
                error_code = result.get('code', 'unknown')
                error_msg = result.get('msg', 'unknown error')
                if error_code == 1106:  # Permission denied
                    print(f"   ⚠️  Permission denied - endpoint may require different access level")
                elif error_code == 1100:  # Invalid parameter
                    print(f"   ⚠️  Invalid parameters - trying without time range...")
                    
                    # Retry without time parameters
                    simple_url = f"{client.api_endpoint}{endpoint}"
                    simple_sig = client._create_signature("GET", simple_url, None, timestamp, client.token)
                    headers['sign'] = simple_sig
                    
                    retry_response = requests.get(simple_url, headers=headers, timeout=10)
                    retry_result = retry_response.json()
                    
                    if retry_result.get('success'):
                        print(f"   ✅ Success without time range")
                        print(f"   📋 Data: {str(retry_result.get('result', {}))[:200]}...")
                    else:
                        print(f"   ❌ Still failed: {retry_result.get('msg', 'unknown')}")
                else:
                    print(f"   ❌ Error {error_code}: {error_msg}")
                    
        except Exception as e:
            print(f"   ❌ Request failed: {e}")

def check_device_data_history():
    """Check what historical information is embedded in current device data"""
    
    client = TuyaWeatherClient()
    print(f"\n=== CHECKING EMBEDDED HISTORICAL DATA ===")
    
    # Get device info
    device_data = client.get_device_data()
    if device_data:
        print(f"Device active since: {datetime.fromtimestamp(device_data.get('active_time', 0))}")
        print(f"Last update: {datetime.fromtimestamp(device_data.get('update_time', 0))}")
    
    # Check status data for timestamps
    status_data = client.get_device_status()
    if status_data and status_data.get('properties'):
        properties = status_data['properties']
        
        # Analyze timestamps in properties
        timestamps = []
        for prop in properties:
            if prop.get('time'):
                timestamps.append({
                    'code': prop.get('code'),
                    'time': datetime.fromtimestamp(prop.get('time') / 1000),
                    'value': prop.get('value')
                })
        
        if timestamps:
            timestamps.sort(key=lambda x: x['time'], reverse=True)
            print(f"\n📅 Recent data points ({len(timestamps)} total):")
            for i, item in enumerate(timestamps[:10]):  # Show last 10
                print(f"   {item['time']} - {item['code']}: {item['value']}")
                if i >= 9:
                    break

if __name__ == "__main__":
    test_garni_historical_endpoints()
    check_device_data_history()