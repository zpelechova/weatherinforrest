#!/usr/bin/env python3
"""
Quick API test to check current status after subscription confirmation
"""

import os
from tuya_client import TuyaWeatherClient

def test_api_status():
    print("=== TUYA API STATUS TEST ===")
    print(f"Testing with credentials:")
    print(f"Access ID: {os.getenv('NEW_TUYA_ACCESS_ID', 'Not set')[:8]}...")
    print(f"Device ID: {os.getenv('NEW_TUYA_DEVICE_ID', 'Not set')}")
    print()
    
    try:
        client = TuyaWeatherClient()
        
        # Test connection
        print("1. Testing API connection...")
        client.test_connection()
        status = client.get_connection_status()
        
        print(f"Connection Status: {status['status']}")
        if status['status'] == 'api_error':
            print(f"Error Details: {status['details']}")
            print(f"Last Error: {status['last_error']}")
        elif status['status'] == 'connected':
            print("✅ API Connection Successful!")
            
            # Try to get device data
            print("\n2. Testing device data retrieval...")
            device_data = client.get_device_data()
            if device_data:
                print("✅ Device data retrieved successfully!")
                print("Available data points:")
                for key, value in device_data.items():
                    print(f"  - {key}: {value}")
            else:
                print("⚠️ No device data available (device may be offline)")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_status()