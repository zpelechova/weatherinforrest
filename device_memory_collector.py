#!/usr/bin/env python3
"""
Access GARNI 925T device memory and cached readings
Many smart weather stations store historical readings locally that can be accessed
"""

import os
import requests
import time
from datetime import datetime, timedelta
from tuya_client import TuyaWeatherClient
from database import WeatherDatabase

class DeviceMemoryCollector:
    """Access GARNI 925T device's internal memory and cached data"""
    
    def __init__(self):
        self.client = TuyaWeatherClient()
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
        self.db = WeatherDatabase()
    
    def extract_all_device_readings(self):
        """Extract all available readings from device memory"""
        print("=== EXTRACTING ALL DEVICE READINGS ===")
        
        if not self.client._get_token():
            print("❌ Failed to get access token")
            return []
        
        # Get comprehensive device status
        device_status = self.client.get_device_status()
        if not device_status or not device_status.get('properties'):
            print("❌ No device properties available")
            return []
        
        properties = device_status['properties']
        print(f"📊 Found {len(properties)} property readings with timestamps")
        
        # Group readings by timestamp to create historical records
        readings_by_time = {}
        
        for prop in properties:
            timestamp = prop.get('time')
            if timestamp:
                timestamp_dt = datetime.fromtimestamp(timestamp / 1000)
                timestamp_key = timestamp_dt.strftime('%Y-%m-%d %H:%M:%S')
                
                if timestamp_key not in readings_by_time:
                    readings_by_time[timestamp_key] = {
                        'timestamp': timestamp_dt,
                        'source': 'garni_925t',
                        'location': 'Kozlovice',
                        'temperature': None,
                        'humidity': None,
                        'pressure': None,
                        'wind_speed': None,
                        'wind_direction': None,
                        'uv_index': None,
                        'brightness': None,
                        'heat_index': None,
                        'dew_point': None,
                        'wind_chill': None,
                        'feels_like': None,
                    }
                
                # Map property codes to weather parameters
                code = prop.get('code', '')
                value = prop.get('value')
                
                if value is not None:
                    reading = readings_by_time[timestamp_key]
                    
                    if code == 'temp_current':
                        reading['temperature'] = value / 10
                    elif code == 'temp_current_external':
                        reading['temperature'] = value / 10
                    elif code == 'humidity_value':
                        reading['humidity'] = value
                    elif code == 'humidity_outdoor':
                        reading['humidity'] = value
                    elif code == 'atmospheric_pressture':
                        reading['pressure'] = value / 100
                    elif code == 'windspeed_avg':
                        reading['wind_speed'] = value / 10
                    elif code == 'windspeed_gust':
                        reading['wind_speed'] = max(reading.get('wind_speed', 0), value / 10)
                    elif code == 'uv_index':
                        reading['uv_index'] = value / 10
                    elif code == 'bright_value':
                        reading['brightness'] = value
                    elif code == 'heat_index':
                        reading['heat_index'] = value / 10
                    elif code == 'dew_point_temp':
                        reading['dew_point'] = value / 10
                    elif code == 'windchill_index':
                        reading['wind_chill'] = value / 10
                    elif code == 'feellike_temp':
                        reading['feels_like'] = value / 10
        
        historical_readings = list(readings_by_time.values())
        print(f"📅 Extracted {len(historical_readings)} unique historical readings")
        
        # Show time range
        if historical_readings:
            timestamps = [r['timestamp'] for r in historical_readings]
            oldest = min(timestamps)
            newest = max(timestamps)
            print(f"📊 Time range: {oldest} to {newest}")
            print(f"⏱️  Span: {(newest - oldest).total_seconds() / 3600:.1f} hours")
        
        return historical_readings
    
    def collect_and_store_device_memory(self):
        """Collect all device readings and store in database"""
        readings = self.extract_all_device_readings()
        
        if not readings:
            print("❌ No historical readings found")
            return False
        
        # Store readings in database
        stored_count = 0
        for reading in readings:
            try:
                # Check if this reading already exists
                existing = self.db.get_data_by_date_range(
                    reading['timestamp'] - timedelta(seconds=30),
                    reading['timestamp'] + timedelta(seconds=30)
                )
                
                if existing.empty:
                    self.db.store_weather_data(reading)
                    stored_count += 1
                    
            except Exception as e:
                print(f"⚠️  Error storing reading: {e}")
                continue
        
        print(f"💾 Stored {stored_count} new readings in database")
        return stored_count > 0
    
    def try_advanced_device_queries(self):
        """Try advanced queries to access more device data"""
        print("\n=== TRYING ADVANCED DEVICE QUERIES ===")
        
        if not self.client._get_token():
            return []
        
        # Try device model-specific endpoints
        advanced_endpoints = [
            # Device info and capabilities
            f"/v2.0/cloud/thing/{self.device_id}",
            f"/v2.0/cloud/thing/{self.device_id}/model",
            f"/v2.0/cloud/thing/{self.device_id}/functions",
            f"/v2.0/cloud/thing/{self.device_id}/status-set",
            
            # Memory and cache endpoints
            f"/v1.0/devices/{self.device_id}/specification",
            f"/v1.0/devices/{self.device_id}/freeze-state",
            f"/v1.0/devices/{self.device_id}/shadow",
            
            # Try with different query parameters
            f"/v2.0/cloud/thing/{self.device_id}/status?include_historic=true",
            f"/v2.0/cloud/thing/{self.device_id}/status?expand=all",
        ]
        
        successful_data = []
        
        for endpoint in advanced_endpoints:
            print(f"\n🔍 Testing: {endpoint}")
            
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
                    print(f"   ✅ SUCCESS: {type(data).__name__} received")
                    
                    if isinstance(data, dict):
                        print(f"      Keys: {list(data.keys())}")
                        # Look for historical data indicators
                        for key, value in data.items():
                            if 'histor' in key.lower() or 'log' in key.lower() or 'cache' in key.lower():
                                print(f"         📊 {key}: {type(value)} ({len(value) if isinstance(value, (list, dict)) else 'scalar'})")
                    
                    successful_data.append({
                        'endpoint': endpoint,
                        'data': data
                    })
                else:
                    error_code = result.get('code', 'unknown')
                    if error_code not in [1108, 1004]:  # Skip common permission errors
                        print(f"   ❌ Error {error_code}: {result.get('msg', 'unknown')}")
                        
            except Exception as e:
                print(f"   ❌ Request failed: {e}")
        
        return successful_data

if __name__ == "__main__":
    collector = DeviceMemoryCollector()
    
    # First, extract all readings from current device status
    print("Step 1: Extracting device memory readings...")
    collector.collect_and_store_device_memory()
    
    # Then try advanced queries
    print("\nStep 2: Trying advanced device queries...")
    advanced_data = collector.try_advanced_device_queries()
    
    if advanced_data:
        print(f"\n✅ Found {len(advanced_data)} additional data sources")
        for item in advanced_data:
            print(f"   - {item['endpoint']}")
    else:
        print("\n⚠️  No additional data sources found")