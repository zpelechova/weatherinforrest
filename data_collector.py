"""Automated data collection from weather station and external APIs."""

import time
import schedule
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import threading

try:
    from meteostat import Point, Hourly, Daily
    METEOSTAT_AVAILABLE = True
except ImportError:
    METEOSTAT_AVAILABLE = False
    logging.warning("Meteostat not available - install with: pip install meteostat")

from tuya_client import TuyaWeatherClient
from local_tuya_client import LocalTuyaWeatherClient
from database import WeatherDatabase
from config import (
    STATION_LATITUDE, STATION_LONGITUDE, 
    COLLECTION_INTERVAL_MINUTES, BACKUP_INTERVAL_HOURS
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDataCollector:
    """Automated weather data collection and storage."""
    
    def __init__(self):
        """Initialize the data collector."""
        self.tuya_client = TuyaWeatherClient()
        self.database = WeatherDatabase()
        self.is_running = False
        self.collection_thread = None
        
        # Initialize Meteostat point if available
        if METEOSTAT_AVAILABLE:
            self.meteostat_point = Point(STATION_LATITUDE, STATION_LONGITUDE)
        else:
            self.meteostat_point = None
    
    def collect_tuya_data(self) -> bool:
        """Collect data from Tuya weather station."""
        try:
            logger.info("Collecting data from Tuya weather station...")
            
            # Try to get device status first (direct device reading)
            device_data = self.tuya_client.get_device_status()
            if device_data:
                parsed_data = self.tuya_client.parse_weather_data(
                    device_data, source="tuya_device"
                )
                if parsed_data:
                    success = self.database.insert_weather_data(parsed_data)
                    if success:
                        logger.info("Successfully stored Tuya device data")
                        return True
            
            # Fallback to weather API
            weather_data = self.tuya_client.get_weather_current(
                STATION_LATITUDE, STATION_LONGITUDE
            )
            if weather_data:
                parsed_data = self.tuya_client.parse_weather_data(
                    weather_data, source="tuya_api"
                )
                if parsed_data:
                    success = self.database.insert_weather_data(parsed_data)
                    if success:
                        logger.info("Successfully stored Tuya weather API data")
                        return True
            
            logger.warning("No data collected from Tuya")
            return False
            
        except Exception as e:
            logger.error(f"Error collecting Tuya data: {e}")
            return False
    
    def collect_meteostat_data(self) -> bool:
        """Collect historical data from Meteostat."""
        if not METEOSTAT_AVAILABLE or not self.meteostat_point:
            return False
        
        try:
            logger.info("Collecting data from Meteostat...")
            
            # Get data for the last hour
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            hourly_data = Hourly(self.meteostat_point, start_time, end_time)
            df = hourly_data.fetch()
            
            if df.empty:
                logger.warning("No Meteostat data available")
                return False
            
            # Process the most recent record
            latest_record = df.iloc[-1]
            
            weather_data = {
                "timestamp": latest_record.name.isoformat(),
                "source": "meteostat",
                "temperature": latest_record.get("temp"),
                "humidity": latest_record.get("rhum"),
                "pressure": latest_record.get("pres"),
                "wind_speed": latest_record.get("wspd"),
                "wind_direction": latest_record.get("wdir"),
                "dew_point": latest_record.get("dwpt"),
                "condition": None  # Meteostat doesn't provide condition text
            }
            
            # Remove None values
            weather_data = {k: v for k, v in weather_data.items() if v is not None}
            
            success = self.database.insert_weather_data(weather_data)
            if success:
                logger.info("Successfully stored Meteostat data")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error collecting Meteostat data: {e}")
            return False
    
    def collect_historical_data(self, days_back: int = 30) -> bool:
        """Collect historical data to fill gaps."""
        if not METEOSTAT_AVAILABLE or not self.meteostat_point:
            logger.warning("Meteostat not available for historical data collection")
            return False
        
        try:
            logger.info(f"Collecting {days_back} days of historical data...")
            
            end_time = datetime.now()
            start_time = end_time - timedelta(days=days_back)
            
            # Use daily data for longer periods
            if days_back > 7:
                daily_data = Daily(self.meteostat_point, start_time, end_time)
                df = daily_data.fetch()
                
                for date, row in df.iterrows():
                    weather_data = {
                        "timestamp": date.isoformat(),
                        "source": "meteostat_daily",
                        "temperature": row.get("tavg"),
                        "humidity": None,  # Not available in daily data
                        "pressure": row.get("pres"),
                        "wind_speed": row.get("wspd"),
                        "wind_direction": row.get("wdir"),
                        "rainfall": row.get("prcp")
                    }
                    
                    # Remove None values
                    weather_data = {k: v for k, v in weather_data.items() if v is not None}
                    self.database.insert_weather_data(weather_data)
            else:
                # Use hourly data for recent periods
                hourly_data = Hourly(self.meteostat_point, start_time, end_time)
                df = hourly_data.fetch()
                
                for timestamp, row in df.iterrows():
                    weather_data = {
                        "timestamp": timestamp.isoformat(),
                        "source": "meteostat_hourly",
                        "temperature": row.get("temp"),
                        "humidity": row.get("rhum"),
                        "pressure": row.get("pres"),
                        "wind_speed": row.get("wspd"),
                        "wind_direction": row.get("wdir"),
                        "dew_point": row.get("dwpt"),
                        "rainfall": row.get("prcp")
                    }
                    
                    # Remove None values
                    weather_data = {k: v for k, v in weather_data.items() if v is not None}
                    self.database.insert_weather_data(weather_data)
            
            logger.info(f"Historical data collection completed for {days_back} days")
            return True
            
        except Exception as e:
            logger.error(f"Error collecting historical data: {e}")
            return False
    
    def run_collection_cycle(self):
        """Run a single data collection cycle - GARNI 925T only."""
        logger.info("Starting data collection cycle from GARNI 925T weather station...")
        
        # Only collect from Tuya weather station
        tuya_success = self.collect_tuya_data()
        
        if not tuya_success:
            logger.error("Failed to collect data from GARNI 925T weather station")
        else:
            logger.info("Successfully collected data from GARNI 925T weather station")
    
    def start_scheduled_collection(self):
        """Start the scheduled data collection."""
        logger.info(f"Starting scheduled data collection every {COLLECTION_INTERVAL_MINUTES} minutes")
        
        # Schedule regular data collection
        schedule.every(COLLECTION_INTERVAL_MINUTES).minutes.do(self.run_collection_cycle)
        
        # Schedule daily cleanup
        schedule.every().day.at("02:00").do(self.database.cleanup_old_data)
        
        self.is_running = True
        
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.collection_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.collection_thread.start()
        
        # Run initial collection
        self.run_collection_cycle()
    
    def stop_scheduled_collection(self):
        """Stop the scheduled data collection."""
        logger.info("Stopping scheduled data collection...")
        self.is_running = False
        schedule.clear()
        
        if self.collection_thread and self.collection_thread.is_alive():
            self.collection_thread.join(timeout=5)
    
    def get_collection_status(self) -> Dict:
        """Get the status of data collection."""
        stats = self.database.get_data_stats()
        tuya_connected = self.tuya_client.test_connection()
        
        return {
            "is_running": self.is_running,
            "tuya_connected": tuya_connected,
            "meteostat_available": METEOSTAT_AVAILABLE,
            "database_stats": stats,
            "last_collection": datetime.now().isoformat()
        }

# Global collector instance
_collector = None

def get_collector() -> WeatherDataCollector:
    """Get the global data collector instance."""
    global _collector
    if _collector is None:
        _collector = WeatherDataCollector()
    return _collector
