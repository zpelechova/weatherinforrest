#!/usr/bin/env python3
"""
Weather monitoring service - checks readings every hour
Provides status reports and alerts for data collection issues
"""

import time
import schedule
import logging
from datetime import datetime, timedelta
from database import WeatherDatabase
from auto_collector_service import get_status
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('weather_monitoring.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class WeatherMonitoringService:
    """Hourly monitoring of weather data collection"""
    
    def __init__(self):
        self.db = WeatherDatabase()
        self.last_check = None
        self.alerts = []
        
    def check_hourly_readings(self):
        """Check if readings were fetched correctly in the last hour"""
        
        logger.info("=== HOURLY WEATHER MONITORING CHECK ===")
        
        try:
            # Get readings from last hour
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=1)
            
            df = self.db.get_data_by_date_range(start_time, end_time)
            garni_df = df[df['source'].str.contains('garni_925t')] if not df.empty else pd.DataFrame()
            
            # Expected readings per hour (288 per day = 12 per hour)
            expected_per_hour = 12
            actual_readings = len(garni_df)
            
            # Collection service status
            service_status = get_status()
            
            # Generate report
            report = {
                'timestamp': end_time,
                'expected_readings': expected_per_hour,
                'actual_readings': actual_readings,
                'collection_rate': (actual_readings / expected_per_hour) * 100 if expected_per_hour > 0 else 0,
                'service_running': service_status['is_running'],
                'status': 'GOOD' if actual_readings >= expected_per_hour * 0.8 else 'WARNING' if actual_readings > 0 else 'CRITICAL'
            }
            
            # Log status
            logger.info(f"Readings check: {actual_readings}/{expected_per_hour} ({report['collection_rate']:.1f}%)")
            logger.info(f"Service status: {'RUNNING' if service_status['is_running'] else 'STOPPED'}")
            logger.info(f"Overall status: {report['status']}")
            
            # Show latest reading if available
            if not garni_df.empty:
                latest = garni_df.sort_values('timestamp').iloc[-1]
                temp = f"{latest.get('temperature', 'N/A')}°C"
                humid = f"{latest.get('humidity', 'N/A')}%"
                pressure = f"{latest.get('pressure', 'N/A')}hPa"
                logger.info(f"Latest reading: {latest['timestamp']} - T={temp}, H={humid}, P={pressure}")
            
            # Generate alerts if needed
            if report['status'] == 'CRITICAL':
                alert = f"CRITICAL: No weather readings in last hour (expected {expected_per_hour})"
                self.alerts.append(alert)
                logger.warning(alert)
            elif report['status'] == 'WARNING':
                alert = f"WARNING: Only {actual_readings}/{expected_per_hour} readings in last hour"
                self.alerts.append(alert)
                logger.warning(alert)
            
            if not service_status['is_running']:
                alert = "ALERT: Auto-collection service is not running"
                self.alerts.append(alert)
                logger.warning(alert)
            
            self.last_check = end_time
            return report
            
        except Exception as e:
            error_msg = f"Error during hourly check: {e}"
            logger.error(error_msg)
            self.alerts.append(error_msg)
            return None
    
    def get_daily_summary(self):
        """Generate daily summary of weather collection"""
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(days=1)
            
            df = self.db.get_data_by_date_range(start_time, end_time)
            garni_df = df[df['source'].str.contains('garni_925t')] if not df.empty else pd.DataFrame()
            
            if garni_df.empty:
                return "No weather data collected in last 24 hours"
            
            # Calculate statistics
            total_readings = len(garni_df)
            expected_daily = 288  # 24 hours * 12 readings per hour
            collection_rate = (total_readings / expected_daily) * 100
            
            # Temperature range
            temp_data = garni_df['temperature'].dropna()
            temp_range = f"{temp_data.min():.1f}°C to {temp_data.max():.1f}°C" if not temp_data.empty else "N/A"
            
            # Humidity range
            humid_data = garni_df['humidity'].dropna()
            humid_range = f"{humid_data.min():.0f}% to {humid_data.max():.0f}%" if not humid_data.empty else "N/A"
            
            summary = f"""
Daily Weather Summary ({start_time.strftime('%Y-%m-%d')}):
- Total readings: {total_readings}/{expected_daily} ({collection_rate:.1f}%)
- Temperature range: {temp_range}
- Humidity range: {humid_range}
- Collection status: {'EXCELLENT' if collection_rate > 90 else 'GOOD' if collection_rate > 70 else 'NEEDS ATTENTION'}
"""
            
            logger.info(summary)
            return summary
            
        except Exception as e:
            error_msg = f"Error generating daily summary: {e}"
            logger.error(error_msg)
            return error_msg
    
    def start_monitoring(self):
        """Start hourly monitoring service"""
        
        logger.info("Starting hourly weather monitoring service...")
        
        # Schedule hourly checks
        schedule.every().hour.do(self.check_hourly_readings)
        
        # Schedule daily summary at 23:00
        schedule.every().day.at("23:00").do(self.get_daily_summary)
        
        # Initial check
        self.check_hourly_readings()
        
        logger.info("Hourly monitoring service started")
        
        # Keep running
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

if __name__ == "__main__":
    monitor = WeatherMonitoringService()
    monitor.start_monitoring()