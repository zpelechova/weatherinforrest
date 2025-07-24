#!/usr/bin/env python3
"""
Investigate Tuya Smart Life app data access methods
The app shows historical data, so we need to find how to access it
"""

import os
import requests
import time
from datetime import datetime, timedelta
from tuya_client import TuyaWeatherClient

class TuyaAppDataInvestigator:
    """Investigate how to access the same data the Smart Life app shows"""
    
    def __init__(self):
        self.client = TuyaWeatherClient()
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
    
    def check_device_capabilities(self):
        """Check what data capabilities the device reports"""
        print("=== DEVICE CAPABILITIES INVESTIGATION ===")
        
        if not self.client._get_token():
            return
        
        # Get comprehensive device information
        device_info_endpoints = [
            f"/v2.0/cloud/thing/{self.device_id}",
            f"/v2.0/cloud/thing/{self.device_id}/model", 
            f"/v2.0/cloud/thing/{self.device_id}/functions",
            f"/v2.0/cloud/thing/{self.device_id}/status-set",
            f"/v1.0/devices/{self.device_id}",
            f"/v1.0/devices/{self.device_id}/specification",
        ]
        
        for endpoint in device_info_endpoints:
            self._test_info_endpoint(endpoint)
    
    def _test_info_endpoint(self, endpoint):
        """Test device information endpoint"""
        
        try:
            timestamp = int(time.time() * 1000)
            signature = self.client._create_signature("GET", f"{self.client.api_endpoint}{endpoint}", None, timestamp, self.client.token)
            
            headers = {
                'client_id': self.client.access_id,
                'access_token': self.client.token,
                't': str(timestamp),
                'sign_method': 'HMAC-SHA256',
                'sign': signature,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(f"{self.client.api_endpoint}{endpoint}", headers=headers, timeout=10)
            result = response.json()
            
            if result.get('success'):
                data = result.get('result', {})
                print(f"\n✅ {endpoint}:")
                
                # Look for relevant information
                relevant_keys = ['functions', 'status', 'model', 'capabilities', 'properties', 'schema', 'dps']
                
                for key in relevant_keys:
                    if key in data:
                        value = data[key]
                        if isinstance(value, (list, dict)):
                            print(f"   {key}: {type(value).__name__} with {len(value) if hasattr(value, '__len__') else 'N/A'} items")
                            if isinstance(value, list) and value:
                                print(f"      Sample: {str(value[0])[:100]}...")
                            elif isinstance(value, dict):
                                print(f"      Keys: {list(value.keys())[:10]}")
                        else:
                            print(f"   {key}: {value}")
                
                # Check for historical data indicators
                data_str = str(data).lower()
                if any(keyword in data_str for keyword in ['history', 'log', 'statistics', 'report', 'data']):
                    print("   🔍 Contains historical data references!")
            
        except Exception as e:
            print(f"❌ {endpoint}: {e}")
    
    def try_alternative_data_formats(self):
        """Try alternative ways to request historical data"""
        print("\n=== ALTERNATIVE DATA REQUEST METHODS ===")
        
        # Try requesting data in different formats/protocols
        alternative_methods = [
            # Different API versions
            ("v1.3", f"/v1.3/devices/{self.device_id}/logs"),
            ("v2.1", f"/v2.1/devices/{self.device_id}/logs"),
            
            # Different content types
            ("json_detailed", f"/v2.0/cloud/thing/{self.device_id}/status?format=detailed"),
            ("export_format", f"/v1.0/devices/{self.device_id}/export"),
            
            # Smart Life app specific endpoints
            ("app_logs", f"/v1.0/smart-life/devices/{self.device_id}/logs"),
            ("app_history", f"/v1.0/smart-life/devices/{self.device_id}/history"),
            
            # Weather station specific
            ("weather_data", f"/v1.0/weather-stations/{self.device_id}/data"),
            ("sensor_logs", f"/v1.0/sensors/{self.device_id}/logs"),
        ]
        
        for method_name, endpoint in alternative_methods:
            print(f"\n🔍 Testing {method_name}: {endpoint}")
            self._test_alternative_endpoint(endpoint)
    
    def _test_alternative_endpoint(self, endpoint):
        """Test alternative endpoint formats"""
        
        # Try different time ranges
        end_time = int(time.time() * 1000)
        time_ranges = [
            ("24h", end_time - (24 * 60 * 60 * 1000)),
            ("7d", end_time - (7 * 24 * 60 * 60 * 1000)),
            ("30d", end_time - (30 * 24 * 60 * 60 * 1000)),
        ]
        
        for period, start_time in time_ranges:
            # Try multiple parameter formats
            param_sets = [
                f"start={start_time}&end={end_time}&limit=1000",
                f"from={start_time}&to={end_time}&count=1000", 
                f"begin={start_time}&finish={end_time}&max=1000",
                f"startTime={start_time}&endTime={end_time}&pageSize=1000",
            ]
            
            for params in param_sets:
                try:
                    url = f"{self.client.api_endpoint}{endpoint}?{params}"
                    timestamp = int(time.time() * 1000)
                    signature = self.client._create_signature("GET", url, None, timestamp, self.client.token)
                    
                    headers = {
                        'client_id': self.client.access_id,
                        'access_token': self.client.token,
                        't': str(timestamp),
                        'sign_method': 'HMAC-SHA256',
                        'sign': signature,
                        'Content-Type': 'application/json'
                    }
                    
                    response = requests.get(url, headers=headers, timeout=10)
                    result = response.json()
                    
                    if result.get('success'):
                        data = result.get('result', {})
                        if data:
                            print(f"   ✅ SUCCESS ({period}): Found data")
                            print(f"      Type: {type(data)}")
                            if hasattr(data, '__len__'):
                                print(f"      Size: {len(data)}")
                            return True
                    
                except Exception as e:
                    continue
        
        return False
    
    def investigate_smart_life_api(self):
        """Investigate Smart Life app API patterns"""
        print("\n=== SMART LIFE APP API INVESTIGATION ===")
        
        # The Smart Life app might use different endpoints
        # Check common mobile app patterns
        
        mobile_endpoints = [
            # Mobile app specific
            f"/v1.0/m/dp/device/{self.device_id}/logs",
            f"/v1.0/mobile/device/{self.device_id}/history", 
            f"/v2.0/app/device/{self.device_id}/data",
            
            # Chart data endpoints (apps often have these)
            f"/v1.0/device/{self.device_id}/chart/data",
            f"/v2.0/device/{self.device_id}/chart/history",
            f"/v1.0/statistics/device/{self.device_id}/chart",
            
            # Export/download endpoints
            f"/v1.0/device/{self.device_id}/export/csv",
            f"/v1.0/device/{self.device_id}/download/history",
        ]
        
        for endpoint in mobile_endpoints:
            print(f"\n📱 Testing mobile endpoint: {endpoint}")
            success = self._test_alternative_endpoint(endpoint)
            if success:
                print(f"   🎉 FOUND WORKING ENDPOINT: {endpoint}")
                return endpoint
        
        return None
    
    def check_subscription_limits(self):
        """Check what the current subscription allows"""
        print("\n=== SUBSCRIPTION LIMITS CHECK ===")
        
        # Check account/subscription info
        account_endpoints = [
            "/v1.0/users/me",
            "/v1.0/apps/subscriptions",
            "/v1.0/apps/quota",
            "/v1.0/account/info",
        ]
        
        for endpoint in account_endpoints:
            try:
                timestamp = int(time.time() * 1000)
                signature = self.client._create_signature("GET", f"{self.client.api_endpoint}{endpoint}", None, timestamp, self.client.token)
                
                headers = {
                    'client_id': self.client.access_id,
                    'access_token': self.client.token,
                    't': str(timestamp),    
                    'sign_method': 'HMAC-SHA256',
                    'sign': signature,
                    'Content-Type': 'application/json'
                }
                
                response = requests.get(f"{self.client.api_endpoint}{endpoint}", headers=headers, timeout=10)
                result = response.json()
                
                if result.get('success'):
                    data = result.get('result', {})
                    print(f"\n✅ {endpoint}:")
                    
                    # Look for subscription/quota information
                    relevant_keys = ['subscription', 'quota', 'limits', 'plan', 'tier', 'permissions']
                    for key in relevant_keys:
                        if key in data:
                            print(f"   {key}: {data[key]}")
            
            except Exception as e:
                print(f"❌ {endpoint}: {e}")

if __name__ == "__main__":
    investigator = TuyaAppDataInvestigator()
    
    print("🔍 Investigating comprehensive data access methods...")
    print("The Smart Life app shows historical data - we need to find how to access it.\n")
    
    investigator.check_device_capabilities()
    investigator.try_alternative_data_formats()
    working_endpoint = investigator.investigate_smart_life_api()
    investigator.check_subscription_limits()
    
    if working_endpoint:
        print(f"\n🎉 Found working historical data endpoint: {working_endpoint}")
        print("This can be used to extract comprehensive historical data!")
    else:
        print("\n💡 RECOMMENDATION:")
        print("The Tuya Cloud API with Trial subscription may not provide access to")
        print("comprehensive historical data that the Smart Life app displays.")
        print("Consider:")
        print("1. Upgrading to Tuya IoT Core subscription")
        print("2. Using local device connection (if supported)")
        print("3. Exporting data from Smart Life app directly")