#!/usr/bin/env python3
"""
Decode and extract historical data from GARNI 925T weather station
The device stores historical data in encoded format in the 'all_max_min' field
"""

import os
import base64
import struct
from datetime import datetime, timedelta
from tuya_client import TuyaWeatherClient
from database import WeatherDatabase

class HistoricalDataDecoder:
    """Decode historical data from GARNI 925T device memory"""
    
    def __init__(self):
        self.client = TuyaWeatherClient()
        self.db = WeatherDatabase()
    
    def extract_all_timestamped_data(self):
        """Extract all data points with their individual timestamps"""
        print("=== EXTRACTING ALL TIMESTAMPED DATA FROM GARNI 925T ===")
        
        status = self.client.get_device_status()
        if not status or not status.get('properties'):
            print("❌ No device data available")
            return []
        
        properties = status['properties']
        historical_readings = []
        
        # Group properties by timestamp
        timestamp_groups = {}
        for prop in properties:
            timestamp = prop.get('time')
            if timestamp:
                ts_key = timestamp
                if ts_key not in timestamp_groups:
                    timestamp_groups[ts_key] = []
                timestamp_groups[ts_key].append(prop)
        
        print(f"📊 Found {len(timestamp_groups)} unique timestamps")
        
        # Convert each timestamp group to a weather reading
        for timestamp, props in timestamp_groups.items():
            try:
                dt = datetime.fromtimestamp(timestamp / 1000)
                
                # Create base weather record
                weather_record = {
                    'timestamp': dt,
                    'source': 'garni_925t_historical',
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
                    'feels_like': None,
                    'wind_chill': None,
                    'rain_rate': None,
                }
                
                # Parse all properties for this timestamp
                for prop in props:
                    code = prop.get('code', '')
                    value = prop.get('value')
                    
                    if value is not None:
                        # Temperature readings
                        if code in ['temp_current', 'temp_current_external'] and isinstance(value, (int, float)):
                            weather_record['temperature'] = value / 10
                        elif code in ['temp_current_external_1', 'temp_current_external_2'] and isinstance(value, (int, float)):
                            weather_record['temperature'] = value / 10
                        
                        # Humidity readings  
                        elif code in ['humidity_value', 'humidity_outdoor'] and isinstance(value, (int, float)):
                            weather_record['humidity'] = value
                        elif code in ['humidity_outdoor_1', 'humidity_outdoor_2'] and isinstance(value, (int, float)):
                            weather_record['humidity'] = value
                        
                        # Pressure readings
                        elif code == 'atmospheric_pressture' and isinstance(value, (int, float)):
                            weather_record['pressure'] = value / 100
                        
                        # Wind readings
                        elif code in ['windspeed_avg', 'windspeed_gust'] and isinstance(value, (int, float)):
                            if weather_record['wind_speed'] is None:
                                weather_record['wind_speed'] = value / 10
                            else:
                                weather_record['wind_speed'] = max(weather_record['wind_speed'], value / 10)
                        
                        # UV Index
                        elif code == 'uv_index' and isinstance(value, (int, float)):
                            weather_record['uv_index'] = value / 10
                        
                        # Other measurements
                        elif code == 'bright_value' and isinstance(value, (int, float)):
                            weather_record['brightness'] = value
                        elif code == 'heat_index' and isinstance(value, (int, float)):
                            weather_record['heat_index'] = value / 10
                        elif code == 'dew_point_temp' and isinstance(value, (int, float)):
                            weather_record['dew_point'] = value / 10
                        elif code == 'feellike_temp' and isinstance(value, (int, float)):
                            weather_record['feels_like'] = value / 10
                        elif code == 'windchill_index' and isinstance(value, (int, float)):
                            weather_record['wind_chill'] = value / 10
                        elif code == 'rain_rate' and isinstance(value, (int, float)):
                            weather_record['rain_rate'] = value / 10
                
                # Only add records with meaningful weather data
                if any(weather_record[param] is not None for param in ['temperature', 'humidity', 'pressure']):
                    historical_readings.append(weather_record)
                    
            except Exception as e:
                print(f"⚠️  Error processing timestamp {timestamp}: {e}")
                continue
        
        # Sort by timestamp
        historical_readings.sort(key=lambda x: x['timestamp'])
        
        if historical_readings:
            oldest = historical_readings[0]['timestamp']
            newest = historical_readings[-1]['timestamp']
            span_days = (newest - oldest).days
            
            print(f"📅 Extracted {len(historical_readings)} historical readings")
            print(f"🗓️  Time span: {oldest.strftime('%Y-%m-%d %H:%M')} to {newest.strftime('%Y-%m-%d %H:%M')}")
            print(f"📊 Coverage: {span_days} days ({span_days/365.25:.1f} years)")
        
        return historical_readings
    
    def decode_all_max_min_data(self):
        """Try to decode the all_max_min field which may contain historical data"""
        print("\n=== DECODING ALL_MAX_MIN HISTORICAL DATA ===")
        
        status = self.client.get_device_status()
        if not status or not status.get('properties'):
            return []
        
        # Find the all_max_min property
        all_max_min_data = None
        for prop in status['properties']:
            if prop.get('code') == 'all_max_min':
                all_max_min_data = prop.get('value')
                break
        
        if not all_max_min_data:
            print("❌ No all_max_min data found")
            return []
        
        print(f"🔍 Found all_max_min data: {len(all_max_min_data)} characters")
        print(f"📋 Sample: {all_max_min_data[:100]}...")
        
        # Try different decoding methods
        decoded_data = []
        
        # Method 1: Base64 decode
        try:
            decoded_bytes = base64.b64decode(all_max_min_data)
            print(f"✅ Base64 decoded: {len(decoded_bytes)} bytes")
            
            # Try to interpret as structured data
            # Weather stations often store data as arrays of values
            
            # Try reading as 16-bit integers (common for weather data)
            if len(decoded_bytes) % 2 == 0:
                values_16bit = struct.unpack(f'>{len(decoded_bytes)//2}H', decoded_bytes)
                print(f"📊 As 16-bit values: {len(values_16bit)} readings")
                print(f"   Sample values: {values_16bit[:20]}")
                
                # Look for patterns that might be temperature/humidity/pressure
                temp_like = [v for v in values_16bit if 0 < v < 500]  # 0-50°C * 10
                humid_like = [v for v in values_16bit if 0 < v <= 100]  # 0-100%
                pressure_like = [v for v in values_16bit if 9000 < v < 11000]  # 900-1100 hPa * 10
                
                print(f"   Potential temperature readings: {len(temp_like)}")
                print(f"   Potential humidity readings: {len(humid_like)}")  
                print(f"   Potential pressure readings: {len(pressure_like)}")
            
            # Try reading as 8-bit values
            values_8bit = struct.unpack(f'{len(decoded_bytes)}B', decoded_bytes)
            print(f"📊 As 8-bit values: first 20: {values_8bit[:20]}")
            
        except Exception as e:
            print(f"❌ Base64 decode failed: {e}")
        
        # Method 2: Hex decode
        try:
            if all(c in '0123456789ABCDEFabcdef' for c in all_max_min_data):
                hex_bytes = bytes.fromhex(all_max_min_data)
                print(f"✅ Hex decoded: {len(hex_bytes)} bytes")
        except Exception as e:
            print(f"❌ Hex decode failed: {e}")
        
        return decoded_data
    
    def store_historical_data(self):
        """Store all extracted historical data in database"""
        print("\n=== STORING HISTORICAL DATA ===")
        
        # Get all timestamped readings
        historical_readings = self.extract_all_timestamped_data()
        
        if not historical_readings:
            print("❌ No historical readings to store")
            return 0
        
        stored_count = 0
        duplicate_count = 0
        
        for reading in historical_readings:
            try:
                # Check if this reading already exists (within 1 minute window)
                existing = self.db.get_data_by_date_range(
                    reading['timestamp'] - timedelta(minutes=1),
                    reading['timestamp'] + timedelta(minutes=1)
                )
                
                if not existing.empty:
                    # Check if it's the same source
                    same_source = existing[existing['source'].str.contains('garni_925t')]
                    if not same_source.empty:
                        duplicate_count += 1
                        continue
                
                # Store new reading
                self.db.insert_weather_data(reading)
                stored_count += 1
                
                if stored_count <= 5:  # Show first 5 stored readings
                    print(f"💾 Stored: {reading['timestamp']} - T:{reading.get('temperature')}, H:{reading.get('humidity')}, P:{reading.get('pressure')}")
                
            except Exception as e:
                print(f"⚠️  Error storing reading from {reading['timestamp']}: {e}")
                continue
        
        print(f"\n✅ Historical data import complete:")
        print(f"   📊 Stored: {stored_count} new readings")
        print(f"   🔄 Skipped: {duplicate_count} duplicates")
        print(f"   📅 Total processed: {len(historical_readings)} readings")
        
        return stored_count

if __name__ == "__main__":
    decoder = HistoricalDataDecoder()
    
    # Extract and decode all available historical data
    decoder.decode_all_max_min_data()
    
    # Store all timestamped data
    stored = decoder.store_historical_data()
    
    if stored > 0:
        print(f"\n🎉 Successfully imported {stored} historical readings from your GARNI 925T!")
        print("   Check your dashboard to see months of historical weather data.")
    else:
        print("\n⚠️  No new historical data was imported.")