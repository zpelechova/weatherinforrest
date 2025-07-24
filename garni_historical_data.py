#!/usr/bin/env python3
"""
Retrieve historical data from GARNI 925T weather station
This module explores various Tuya API endpoints to access months of historical data
"""

import os
import requests
import time
from datetime import datetime, timedelta
from tuya_client import TuyaWeatherClient
from database import WeatherDatabase

class GarniHistoricalDataCollector:
    """Collect historical data from GARNI 925T weather station via Tuya API"""
    
    def __init__(self):
        self.client = TuyaWeatherClient()
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
        self.db = WeatherDatabase()
    
    def explore_historical_endpoints(self):
        """Test various historical data endpoints"""
        print("=== EXPLORING GARNI 925T HISTORICAL DATA ENDPOINTS ===")
        
        if not self.client._get_token():
            print("❌ Failed to get access token")
            return []
        
        # Various historical data endpoints to test
        historical_endpoints = [
            # Standard device logs
            f"/v1.0/devices/{self.device_id}/logs",
            f"/v1.0/devices/{self.device_id}/status/logs", 
            f"/v1.0/devices/{self.device_id}/properties/logs",
            
            # IoT Cloud endpoints
            f"/v2.0/cloud/thing/{self.device_id}/logs",
            f"/v2.0/cloud/thing/{self.device_id}/shadow/properties/logs",
            f"/v2.0/cloud/thing/{self.device_id}/status/logs",
            
            # Statistics endpoints
            f"/v1.0/devices/{self.device_id}/statistics",
            f"/v1.0/devices/{self.device_id}/statistics/days",
            f"/v1.0/devices/{self.device_id}/statistics/months",
            
            # Data points endpoints
            f"/v1.0/devices/{self.device_id}/data-points",
            f"/v2.0/cloud/thing/{self.device_id}/data-points",
            
            # Historical statistics
            f"/v1.0/devices/{self.device_id}/history",
            f"/v2.0/devices/{self.device_id}/history",
        ]
        
        successful_endpoints = []
        
        for endpoint in historical_endpoints:
            print(f"\n📊 Testing: {endpoint}")
            
            # Test with different time ranges
            end_time = int(time.time() * 1000)
            
            # Try different historical periods
            time_ranges = [
                ("1 day", end_time - (24 * 60 * 60 * 1000)),
                ("1 week", end_time - (7 * 24 * 60 * 60 * 1000)),
                ("1 month", end_time - (30 * 24 * 60 * 60 * 1000)),
                ("3 months", end_time - (90 * 24 * 60 * 60 * 1000)),
            ]
            
            for period_name, start_time in time_ranges:
                success = self._test_endpoint_with_time_range(endpoint, start_time, end_time, period_name)
                if success:
                    successful_endpoints.append({
                        'endpoint': endpoint,
                        'period': period_name,
                        'start_time': start_time,
                        'end_time': end_time
                    })
                    break  # Found working time range for this endpoint
        
        return successful_endpoints
    
    def _test_endpoint_with_time_range(self, endpoint, start_time, end_time, period_name):
        """Test a specific endpoint with time range parameters"""
        
        # Try different parameter formats
        param_formats = [
            # Standard format
            f"start_time={start_time}&end_time={end_time}&limit=100",
            # Alternative formats
            f"startTime={start_time}&endTime={end_time}&size=100",
            f"from={start_time}&to={end_time}&limit=100",
            f"begin_time={start_time}&end_time={end_time}&limit=100",
            # Without limit
            f"start_time={start_time}&end_time={end_time}",
            # Just with limit
            "limit=100",
            # No parameters (recent data)
            ""
        ]
        
        for params in param_formats:
            try:
                url = f"{self.client.api_endpoint}{endpoint}"
                if params:
                    url += f"?{params}"
                
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
                    
                    if isinstance(data, list) and data:
                        print(f"   ✅ SUCCESS ({period_name}): Found {len(data)} records")
                        print(f"      Parameters: {params}")
                        print(f"      Sample: {str(data[0])[:150]}...")
                        return True
                    elif isinstance(data, dict) and data:
                        print(f"   ✅ SUCCESS ({period_name}): Found data structure")
                        print(f"      Parameters: {params}")
                        print(f"      Keys: {list(data.keys())}")
                        return True
                
            except Exception as e:
                continue  # Try next parameter format
        
        return False
    
    def collect_historical_data_batch(self, days_back=90):
        """Collect historical data in batches"""
        print(f"\n=== COLLECTING {days_back} DAYS OF HISTORICAL DATA ===")
        
        successful_endpoints = self.explore_historical_endpoints()
        
        if not successful_endpoints:
            print("❌ No working historical endpoints found")
            return False
        
        print(f"\n✅ Found {len(successful_endpoints)} working endpoints")
        
        # Use the best endpoint for data collection
        best_endpoint = successful_endpoints[0]  # Use first successful one
        print(f"📊 Using endpoint: {best_endpoint['endpoint']}")
        
        return self._collect_from_endpoint(best_endpoint, days_back)
    
    def _collect_from_endpoint(self, endpoint_info, days_back):
        """Collect data from a specific working endpoint"""
        
        endpoint = endpoint_info['endpoint']
        end_time = int(time.time() * 1000)
        start_time = end_time - (days_back * 24 * 60 * 60 * 1000)
        
        url = f"{self.client.api_endpoint}{endpoint}?start_time={start_time}&end_time={end_time}&limit=1000"
        
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
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            result = response.json()
            
            if result.get('success'):
                historical_data = result.get('result', [])
                print(f"✅ Retrieved {len(historical_data)} historical records")
                
                # Store in database
                stored_count = self._store_historical_data(historical_data)
                print(f"💾 Stored {stored_count} new records in database")
                
                return True
            else:
                print(f"❌ API Error: {result.get('msg', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Request failed: {e}")
            return False
    
    def _store_historical_data(self, historical_data):
        """Store historical data in database with proper formatting"""
        
        stored_count = 0
        
        for record in historical_data:
            try:
                # Parse the historical record format
                timestamp = record.get('time') or record.get('timestamp')
                if timestamp:
                    # Convert timestamp to datetime
                    if isinstance(timestamp, int):
                        timestamp = datetime.fromtimestamp(timestamp / 1000)
                    else:
                        timestamp = datetime.fromisoformat(str(timestamp).replace('Z', ''))
                    
                    # Extract weather parameters
                    weather_data = {
                        'timestamp': timestamp,
                        'source': 'garni_925t_historical',
                        'location': 'Kozlovice',
                        'temperature': None,
                        'humidity': None,
                        'pressure': None,
                        'wind_speed': None,
                        'wind_direction': None,
                        'uv_index': None,
                    }
                    
                    # Parse data based on record structure
                    if 'properties' in record:
                        properties = record['properties']
                    elif 'data' in record:
                        properties = record['data']
                    else:
                        properties = record
                    
                    # Extract known parameters
                    for prop in properties if isinstance(properties, list) else [properties]:
                        if isinstance(prop, dict):
                            code = prop.get('code', '')
                            value = prop.get('value')
                            
                            if code == 'temp_current' and value is not None:
                                weather_data['temperature'] = value / 10
                            elif code == 'temp_current_external' and value is not None:
                                weather_data['temperature'] = value / 10
                            elif code == 'humidity_value' and value is not None:
                                weather_data['humidity'] = value
                            elif code == 'humidity_outdoor' and value is not None:
                                weather_data['humidity'] = value
                            elif code == 'atmospheric_pressture' and value is not None:
                                weather_data['pressure'] = value / 100
                            elif code == 'windspeed_avg' and value is not None:
                                weather_data['wind_speed'] = value / 10
                            elif code == 'uv_index' and value is not None:
                                weather_data['uv_index'] = value / 10
                    
                    # Store if we have valid data
                    if any(weather_data[k] is not None for k in ['temperature', 'humidity', 'pressure']):
                        self.db.store_weather_data(weather_data)
                        stored_count += 1
                        
            except Exception as e:
                print(f"⚠️  Error storing record: {e}")
                continue
        
        return stored_count

if __name__ == "__main__":
    collector = GarniHistoricalDataCollector()
    
    # First explore what's available
    collector.explore_historical_endpoints()
    
    # Then try to collect historical data
    collector.collect_historical_data_batch(days_back=90)