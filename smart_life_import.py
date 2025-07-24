#!/usr/bin/env python3
"""
Smart Life app historical data import system
Processes and imports historical weather data from Smart Life app exports
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from database import WeatherDatabase
import logging

logger = logging.getLogger(__name__)

class SmartLifeImporter:
    """Import historical weather data from Smart Life app exports"""
    
    def __init__(self):
        self.db = WeatherDatabase()
        self.supported_formats = {
            'timestamp_formats': [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d %H:%M',
                '%m/%d/%Y %H:%M:%S',
                '%m/%d/%Y %H:%M',
                '%d/%m/%Y %H:%M:%S',
                '%d/%m/%Y %H:%M',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%dT%H:%M:%SZ',
                '%Y-%m-%d',
                '%m/%d/%Y',
                '%d/%m/%Y'
            ],
            'parameter_mappings': {
                # Temperature variations
                'temp': 'temperature',
                'temperature': 'temperature',
                'temp_current': 'temperature',
                'current_temp': 'temperature',
                'air_temp': 'temperature',
                'outdoor_temp': 'temperature',
                
                # Humidity variations
                'humid': 'humidity',
                'humidity': 'humidity',
                'humid_current': 'humidity',
                'current_humid': 'humidity',
                'rh': 'humidity',
                'relative_humidity': 'humidity',
                
                # Pressure variations
                'press': 'pressure',
                'pressure': 'pressure',
                'barometric_pressure': 'pressure',
                'atmospheric_pressure': 'pressure',
                'press_current': 'pressure',
                
                # Wind variations
                'wind': 'wind_speed',
                'wind_speed': 'wind_speed',
                'wind_velocity': 'wind_speed',
                'windspeed': 'wind_speed',
                
                # UV variations
                'uv': 'uv_index',
                'uv_index': 'uv_index',
                'ultraviolet': 'uv_index',
                'uv_level': 'uv_index'
            }
        }
    
    def analyze_file_structure(self, df):
        """Analyze the structure of imported data file"""
        
        analysis = {
            'total_rows': len(df),
            'columns': list(df.columns),
            'column_count': len(df.columns),
            'data_types': df.dtypes.to_dict(),
            'sample_data': df.head(3).to_dict(),
            'timestamp_columns': [],
            'weather_columns': [],
            'date_range': None,
            'suspected_format': 'unknown'
        }
        
        # Find timestamp columns
        for col in df.columns:
            col_lower = col.lower()
            sample_values = df[col].dropna().head(10).astype(str)
            
            # Check if column contains timestamp-like data
            if any(keyword in col_lower for keyword in ['time', 'date', 'timestamp', 'datetime']):
                analysis['timestamp_columns'].append(col)
            elif self._looks_like_timestamp(sample_values):
                analysis['timestamp_columns'].append(col)
        
        # Find weather parameter columns
        for col in df.columns:
            col_lower = col.lower().replace('_', '').replace(' ', '')
            if col_lower in self.supported_formats['parameter_mappings']:
                analysis['weather_columns'].append({
                    'original': col,
                    'mapped': self.supported_formats['parameter_mappings'][col_lower]
                })
        
        # Determine suspected format
        if analysis['timestamp_columns'] and analysis['weather_columns']:
            analysis['suspected_format'] = 'standard_weather_export'
        elif len(df.columns) >= 3:
            analysis['suspected_format'] = 'possible_weather_data'
        
        return analysis
    
    def _looks_like_timestamp(self, sample_values):
        """Check if values look like timestamps"""
        
        timestamp_indicators = [
            r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
            r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
            r'\d{2}:\d{2}:\d{2}',  # HH:MM:SS
            r'\d{10,13}',          # Unix timestamp
        ]
        
        import re
        for value in sample_values:
            value_str = str(value)
            if any(re.search(pattern, value_str) for pattern in timestamp_indicators):
                return True
        
        return False
    
    def parse_timestamps(self, df, timestamp_column):
        """Parse timestamps from various formats"""
        
        timestamps = []
        
        for index, value in df[timestamp_column].items():
            if pd.isna(value):
                timestamps.append(None)
                continue
            
            value_str = str(value).strip()
            
            # Try Unix timestamp first
            try:
                if value_str.isdigit() and len(value_str) >= 10:
                    timestamp_val = int(value_str)
                    if timestamp_val > 1000000000:  # Valid Unix timestamp range
                        if len(value_str) > 10:  # Milliseconds
                            timestamp_val = timestamp_val / 1000
                        dt = datetime.fromtimestamp(timestamp_val)
                        timestamps.append(dt)
                        continue
            except:
                pass
            
            # Try various datetime formats
            parsed = False
            for fmt in self.supported_formats['timestamp_formats']:
                try:
                    dt = datetime.strptime(value_str, fmt)
                    timestamps.append(dt)
                    parsed = True
                    break
                except:
                    continue
            
            if not parsed:
                timestamps.append(None)
        
        return timestamps
    
    def process_weather_data(self, df, analysis):
        """Process and normalize weather data"""
        
        processed_records = []
        
        # Determine timestamp column
        timestamp_col = None
        if analysis['timestamp_columns']:
            timestamp_col = analysis['timestamp_columns'][0]  # Use first timestamp column
        
        if not timestamp_col:
            logger.error("No timestamp column found")
            return []
        
        # Parse timestamps
        timestamps = self.parse_timestamps(df, timestamp_col)
        
        # Process each row
        for index, row in df.iterrows():
            timestamp = timestamps[index]
            if not timestamp:
                continue
            
            # Build weather record
            record = {
                'timestamp': timestamp,
                'source': 'garni_925t_smartlife_import',
                'location': 'Kozlovice'
            }
            
            # Map weather parameters
            for weather_col in analysis['weather_columns']:
                original_col = weather_col['original']
                mapped_param = weather_col['mapped']
                
                value = row[original_col]
                if pd.notna(value):
                    try:
                        # Convert to numeric
                        numeric_value = float(value)
                        
                        # Apply unit conversions if needed
                        if mapped_param == 'temperature':
                            # Assume Celsius, but check for Fahrenheit
                            if numeric_value > 50:  # Likely Fahrenheit
                                numeric_value = (numeric_value - 32) * 5/9
                        
                        record[mapped_param] = numeric_value
                        
                    except:
                        continue
            
            # Only add record if it has at least one weather parameter
            weather_params = ['temperature', 'humidity', 'pressure', 'wind_speed', 'uv_index']
            if any(param in record for param in weather_params):
                processed_records.append(record)
        
        return processed_records
    
    def import_historical_data(self, file_path_or_df):
        """Import historical data from file or DataFrame"""
        
        try:
            # Load data
            if isinstance(file_path_or_df, str):
                if file_path_or_df.endswith('.csv'):
                    df = pd.read_csv(file_path_or_df)
                else:
                    df = pd.read_excel(file_path_or_df)
            else:
                df = file_path_or_df
            
            logger.info(f"Loaded file with {len(df)} rows and {len(df.columns)} columns")
            
            # Analyze structure
            analysis = self.analyze_file_structure(df)
            logger.info(f"Detected format: {analysis['suspected_format']}")
            
            if analysis['suspected_format'] == 'unknown':
                return {
                    'success': False,
                    'error': 'Could not determine data format',
                    'analysis': analysis
                }
            
            # Process weather data
            processed_records = self.process_weather_data(df, analysis)
            logger.info(f"Processed {len(processed_records)} weather records")
            
            if not processed_records:
                return {
                    'success': False,
                    'error': 'No valid weather data found',
                    'analysis': analysis
                }
            
            # Import to database
            imported_count = 0
            skipped_count = 0
            
            for record in processed_records:
                try:
                    # Check for duplicates
                    existing = self.db.get_data_by_date_range(
                        record['timestamp'] - timedelta(minutes=30),
                        record['timestamp'] + timedelta(minutes=30)
                    )
                    
                    # Filter to same source to avoid conflicts with regular collection
                    existing_same_source = existing[
                        existing['source'].str.contains('smartlife_import')
                    ] if not existing.empty else pd.DataFrame()
                    
                    if existing_same_source.empty:
                        self.db.insert_weather_data(record)
                        imported_count += 1
                    else:
                        skipped_count += 1
                        
                except Exception as e:
                    logger.error(f"Error importing record: {e}")
                    continue
            
            return {
                'success': True,
                'imported_count': imported_count,
                'skipped_count': skipped_count,
                'total_processed': len(processed_records),
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Import error: {e}")
            return {
                'success': False,
                'error': str(e),
                'analysis': None
            }

if __name__ == "__main__":
    importer = SmartLifeImporter()
    
    # Test with sample data structure
    print("Smart Life Historical Data Importer")
    print("Supports CSV and Excel files from Smart Life app export")
    print("Ready to process weather station historical data")