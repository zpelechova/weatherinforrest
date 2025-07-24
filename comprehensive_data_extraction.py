#!/usr/bin/env python3
"""
Comprehensive historical data extraction from GARNI 925T weather station
Extract complete daily/hourly datasets, not just sparse readings
"""

import os
import requests
import time
import base64
import struct
from datetime import datetime, timedelta
from tuya_client import TuyaWeatherClient
from database import WeatherDatabase

class ComprehensiveDataExtractor:
    """Extract complete historical datasets from GARNI 925T"""
    
    def __init__(self):
        self.client = TuyaWeatherClient()
        self.device_id = os.getenv('NEW_TUYA_DEVICE_ID')
        self.db = WeatherDatabase()
    
    def explore_device_statistics_endpoints(self):
        """Check device statistics endpoints that might contain daily/hourly aggregates"""
        print("=== EXPLORING DEVICE STATISTICS FOR HISTORICAL DATA ===")
        
        if not self.client._get_token():
            print("❌ Failed to get access token")
            return []
        
        # Statistics endpoints that might contain historical aggregates
        stats_endpoints = [
            # Daily statistics
            f"/v1.0/devices/{self.device_id}/statistics/days",
            f"/v2.0/devices/{self.device_id}/statistics/days", 
            f"/v1.0/devices/{self.device_id}/logs/statistics/days",
            
            # Monthly statistics
            f"/v1.0/devices/{self.device_id}/statistics/months",
            f"/v2.0/devices/{self.device_id}/statistics/months",
            
            # Raw logs with pagination
            f"/v1.0/devices/{self.device_id}/logs",
            f"/v2.0/devices/{self.device_id}/logs",
            f"/v1.0/devices/{self.device_id}/properties/logs",
            
            # Device data points
            f"/v1.0/devices/{self.device_id}/data-points",
            f"/v2.0/devices/{self.device_id}/data-points",
            
            # Historical data endpoints
            f"/v1.0/devices/{self.device_id}/history/data",
            f"/v2.0/devices/{self.device_id}/history",
            f"/v1.0/devices/{self.device_id}/reports",
        ]
        
        successful_endpoints = []
        
        for endpoint in stats_endpoints:
            print(f"\n📊 Testing: {endpoint}")
            
            # Test with various time ranges and parameters
            time_ranges = [
                ("1 day", 1),
                ("7 days", 7), 
                ("30 days", 30),
                ("90 days", 90),
                ("365 days", 365),
            ]
            
            for period_name, days in time_ranges:
                success = self._test_stats_endpoint(endpoint, days, period_name)
                if success:
                    successful_endpoints.append({
                        'endpoint': endpoint,
                        'period': period_name,
                        'days': days
                    })
                    break  # Found working configuration
        
        return successful_endpoints
    
    def _test_stats_endpoint(self, endpoint, days, period_name):
        """Test statistics endpoint with various parameter combinations"""
        
        end_time = int(time.time() * 1000)
        start_time = end_time - (days * 24 * 60 * 60 * 1000)
        
        # Different parameter formats for statistics
        param_sets = [
            # Standard time range
            f"start_time={start_time}&end_time={end_time}&type=1&limit=1000",
            f"start_time={start_time}&end_time={end_time}&stat_type=sum&limit=1000",
            f"startTime={start_time}&endTime={end_time}&size=1000",
            
            # Daily aggregation
            f"start_time={start_time}&end_time={end_time}&granularity=day&limit=100",
            f"start_time={start_time}&end_time={end_time}&period=daily&limit=100",
            
            # Hourly aggregation  
            f"start_time={start_time}&end_time={end_time}&granularity=hour&limit=2400",
            f"start_time={start_time}&end_time={end_time}&period=hourly&limit=2400",
            
            # Raw logs with pagination
            f"start_time={start_time}&end_time={end_time}&page_no=1&page_size=1000",
            f"start_time={start_time}&end_time={end_time}&offset=0&limit=1000",
            
            # Simple parameters
            f"limit=1000",
            f"size=1000", 
            f"count=1000",
            ""  # No parameters
        ]
        
        for params in param_sets:
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
                
                response = requests.get(url, headers=headers, timeout=15)
                result = response.json()
                
                if result.get('success'):
                    data = result.get('result', {})
                    
                    if isinstance(data, list) and len(data) > 10:  # Substantial data
                        print(f"   ✅ SUCCESS ({period_name}): {len(data)} records")
                        print(f"      Parameters: {params}")
                        print(f"      Sample: {str(data[0])[:100]}...")
                        return True
                    elif isinstance(data, dict) and data:
                        # Check for nested arrays or data structures
                        for key, value in data.items():
                            if isinstance(value, list) and len(value) > 10:
                                print(f"   ✅ SUCCESS ({period_name}): {len(value)} records in '{key}'")
                                print(f"      Parameters: {params}")
                                return True
                
            except Exception as e:
                continue  # Try next parameter set
        
        return False
    
    def decode_all_max_min_comprehensive(self):
        """More comprehensive decoding of the all_max_min field"""
        print("\n=== COMPREHENSIVE ALL_MAX_MIN DECODING ===")
        
        status = self.client.get_device_status()
        if not status or not status.get('properties'):
            return []
        
        # Find all encoded data fields
        encoded_fields = []
        for prop in status['properties']:
            code = prop.get('code', '')
            value = prop.get('value')
            
            if value and isinstance(value, str) and len(value) > 20:
                # Looks like encoded data
                encoded_fields.append({
                    'code': code,
                    'value': value,
                    'length': len(value)
                })
        
        print(f"🔍 Found {len(encoded_fields)} encoded data fields:")
        for field in encoded_fields:
            print(f"   {field['code']}: {field['length']} characters")
        
        historical_records = []
        
        for field in encoded_fields:
            print(f"\n📊 Decoding {field['code']}...")
            records = self._decode_binary_weather_data(field['value'], field['code'])
            historical_records.extend(records)
        
        return historical_records
    
    def _decode_binary_weather_data(self, encoded_data, field_name):
        """Decode binary weather data from various encoded formats"""
        
        records = []
        
        try:
            # Try Base64 decoding
            decoded_bytes = base64.b64decode(encoded_data)
            print(f"   ✅ Base64 decoded: {len(decoded_bytes)} bytes")
            
            # Weather stations often use specific data structures
            # Try interpreting as time-series data
            
            if len(decoded_bytes) >= 8:  # Minimum for timestamp + value
                
                # Pattern 1: 4-byte timestamp + 2-byte values repeating
                if len(decoded_bytes) % 6 == 0:
                    record_count = len(decoded_bytes) // 6
                    print(f"   📊 Trying 6-byte records: {record_count} potential readings")
                    
                    for i in range(min(record_count, 1000)):  # Limit to 1000 records
                        offset = i * 6
                        try:
                            timestamp = struct.unpack('>I', decoded_bytes[offset:offset+4])[0]
                            value = struct.unpack('>H', decoded_bytes[offset+4:offset+6])[0]
                            
                            # Convert timestamp (if reasonable)
                            if 1500000000 < timestamp < 2000000000:  # Reasonable Unix timestamp range
                                dt = datetime.fromtimestamp(timestamp)
                                
                                # Interpret value based on field name and range
                                interpreted_value = self._interpret_weather_value(value, field_name)
                                
                                if interpreted_value:
                                    records.append({
                                        'timestamp': dt,
                                        'source': f'garni_925t_{field_name}',
                                        'location': 'Kozlovice',
                                        **interpreted_value
                                    })
                        except:
                            continue
                
                # Pattern 2: 8-byte records (4-byte timestamp + 4-byte value)
                elif len(decoded_bytes) % 8 == 0:
                    record_count = len(decoded_bytes) // 8
                    print(f"   📊 Trying 8-byte records: {record_count} potential readings")
                    
                    for i in range(min(record_count, 1000)):
                        offset = i * 8
                        try:
                            timestamp = struct.unpack('>I', decoded_bytes[offset:offset+4])[0]
                            value = struct.unpack('>I', decoded_bytes[offset+4:offset+8])[0]
                            
                            if 1500000000 < timestamp < 2000000000:
                                dt = datetime.fromtimestamp(timestamp)
                                interpreted_value = self._interpret_weather_value(value, field_name)
                                
                                if interpreted_value:
                                    records.append({
                                        'timestamp': dt,
                                        'source': f'garni_925t_{field_name}',
                                        'location': 'Kozlovice',
                                        **interpreted_value
                                    })
                        except:
                            continue
                
                # Pattern 3: Array of 16-bit values (measurements without timestamps)
                else:
                    values_16bit = struct.unpack(f'>{len(decoded_bytes)//2}H', decoded_bytes)
                    print(f"   📊 16-bit values: {len(values_16bit)} readings")
                    
                    # Generate timestamps assuming regular intervals
                    base_time = datetime.now() - timedelta(hours=len(values_16bit))
                    
                    for i, value in enumerate(values_16bit[:1000]):  # Limit to 1000
                        interpreted_value = self._interpret_weather_value(value, field_name)
                        if interpreted_value:
                            records.append({
                                'timestamp': base_time + timedelta(hours=i),
                                'source': f'garni_925t_{field_name}',
                                'location': 'Kozlovice',
                                **interpreted_value
                            })
            
            if records:
                print(f"   ✅ Decoded {len(records)} historical records from {field_name}")
                # Show sample
                if records:
                    sample = records[0]
                    print(f"      Sample: {sample['timestamp']} - {list(sample.keys())[3:6]}")
            
        except Exception as e:
            print(f"   ❌ Decoding failed: {e}")
        
        return records
    
    def _interpret_weather_value(self, value, field_name):
        """Interpret numeric values as weather parameters based on context"""
        
        # Different interpretations based on field name and value range
        result = {}
        
        if 'temp' in field_name.lower() or 'all' in field_name.lower():
            # Temperature values (usually stored as tenths)
            if 0 < value < 500:  # 0-50°C
                result['temperature'] = value / 10.0
            elif 1000 < value < 1500:  # Fahrenheit to Celsius
                result['temperature'] = (value/10 - 32) * 5/9
        
        if 'humid' in field_name.lower() or 'all' in field_name.lower():
            # Humidity values (0-100%)
            if 0 <= value <= 100:
                result['humidity'] = float(value)
            elif 100 < value <= 1000:  # Stored as tenths
                result['humidity'] = value / 10.0
        
        if 'press' in field_name.lower() or 'all' in field_name.lower():
            # Pressure values (usually in tenths of hPa)
            if 9000 <= value <= 11000:  # 900-1100 hPa in tenths
                result['pressure'] = value / 100.0
            elif 900 <= value <= 1100:  # Direct hPa
                result['pressure'] = float(value)
        
        if 'wind' in field_name.lower() or 'all' in field_name.lower():
            # Wind speed (usually in tenths of m/s)
            if 0 <= value <= 500:  # 0-50 m/s in tenths
                result['wind_speed'] = value / 10.0
        
        if 'uv' in field_name.lower() or 'all' in field_name.lower():
            # UV index (usually in tenths)
            if 0 <= value <= 150:  # 0-15 UV index in tenths
                result['uv_index'] = value / 10.0
        
        return result if result else None
    
    def run_comprehensive_extraction(self):
        """Run complete historical data extraction"""
        print("=== COMPREHENSIVE GARNI DATA EXTRACTION ===")
        
        total_imported = 0
        
        # Step 1: Try statistics endpoints
        print("Step 1: Checking statistics endpoints...")
        stats_endpoints = self.explore_device_statistics_endpoints()
        if stats_endpoints:
            print(f"Found {len(stats_endpoints)} working statistics endpoints")
            # TODO: Extract data from these endpoints
        
        # Step 2: Comprehensive binary data decoding
        print("\nStep 2: Comprehensive binary data decoding...")
        historical_records = self.decode_all_max_min_comprehensive()
        
        if historical_records:
            print(f"📊 Decoded {len(historical_records)} historical records")
            
            # Store in database
            stored_count = 0
            for record in historical_records:
                try:
                    # Check for duplicates
                    existing = self.db.get_data_by_date_range(
                        record['timestamp'] - timedelta(minutes=30),
                        record['timestamp'] + timedelta(minutes=30)
                    )
                    
                    if existing.empty:
                        self.db.insert_weather_data(record)
                        stored_count += 1
                        
                        if stored_count <= 10:  # Show first 10
                            params = [k for k in record.keys() if k not in ['timestamp', 'source', 'location'] and record[k] is not None]
                            print(f"💾 {record['timestamp']}: {params}")
                            
                except Exception as e:
                    continue
            
            total_imported += stored_count
            print(f"✅ Imported {stored_count} new historical records")
        
        return total_imported

if __name__ == "__main__":
    extractor = ComprehensiveDataExtractor()
    imported = extractor.run_comprehensive_extraction()
    
    if imported > 0:
        print(f"\n🎉 SUCCESS: Imported {imported} comprehensive historical records!")
        print("Your dashboard now has much more complete historical data.")
    else:
        print("\n⚠️  No additional comprehensive data found.")
        print("Your GARNI 925T may store data differently or require specific API access.")