#!/usr/bin/env python3
"""
Persistent weather collection service - runs independently of main app
Ensures continuous data collection regardless of Streamlit app restarts
"""

import time
import schedule
import logging
import threading
import signal
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Import our modules
from data_collector import WeatherDataCollector
from database import WeatherDatabase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('persistent_weather.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PersistentWeatherService:
    """Independent weather collection service that runs continuously"""
    
    def __init__(self):
        self.collector = WeatherDataCollector()
        self.db = WeatherDatabase()
        self.running = False
        self.collection_thread = None
        self.stats = {
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'start_time': None,
            'last_collection': None,
            'last_success': None
        }
        
        # Create status file
        self.status_file = Path('weather_service_status.txt')
        
    def collect_weather_data(self):
        """Collect weather data and update statistics"""
        
        try:
            logger.info("Starting weather data collection...")
            self.stats['total_collections'] += 1
            self.stats['last_collection'] = datetime.now()
            
            # Collect from Tuya device
            success = self.collector.collect_tuya_data()
            
            if success:
                self.stats['successful_collections'] += 1
                self.stats['last_success'] = datetime.now()
                
                # Get latest data to show in logs
                latest = self.db.get_latest_data(limit=1)
                if not latest.empty:
                    row = latest.iloc[0]
                    temp = f"{row.get('temperature', 'N/A')}°C"
                    humid = f"{row.get('humidity', 'N/A')}%"
                    pressure = f"{row.get('pressure', 'N/A')}hPa"
                    logger.info(f"✅ Collection successful: T={temp}, H={humid}, P={pressure}")
                else:
                    logger.info("✅ Collection successful")
            else:
                self.stats['failed_collections'] += 1
                logger.warning("❌ Collection failed")
                
            # Update status file
            self.update_status_file()
            
        except Exception as e:
            self.stats['failed_collections'] += 1
            logger.error(f"Collection error: {e}")
            self.update_status_file()
    
    def update_status_file(self):
        """Update status file with current statistics"""
        
        try:
            success_rate = 0
            if self.stats['total_collections'] > 0:
                success_rate = (self.stats['successful_collections'] / self.stats['total_collections']) * 100
            
            uptime = ""
            if self.stats['start_time']:
                uptime_delta = datetime.now() - self.stats['start_time']
                hours = int(uptime_delta.total_seconds() // 3600)
                minutes = int((uptime_delta.total_seconds() % 3600) // 60)
                uptime = f"{hours}h {minutes}m"
            
            status_content = f"""PERSISTENT WEATHER SERVICE STATUS
=================================
Status: {'RUNNING' if self.running else 'STOPPED'}
Started: {self.stats['start_time'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['start_time'] else 'Never'}
Uptime: {uptime}
Total Collections: {self.stats['total_collections']}
Successful: {self.stats['successful_collections']}
Failed: {self.stats['failed_collections']}
Success Rate: {success_rate:.1f}%
Last Collection: {self.stats['last_collection'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['last_collection'] else 'Never'}
Last Success: {self.stats['last_success'].strftime('%Y-%m-%d %H:%M:%S') if self.stats['last_success'] else 'Never'}
Next Collection: {datetime.now() + timedelta(minutes=5)}
PID: {os.getpid()}
"""
            
            with open(self.status_file, 'w') as f:
                f.write(status_content)
                
        except Exception as e:
            logger.error(f"Failed to update status file: {e}")
    
    def start_service(self):
        """Start the persistent weather collection service"""
        
        if self.running:
            logger.info("Service already running")
            return
        
        logger.info("=== STARTING PERSISTENT WEATHER SERVICE ===")
        logger.info("Collection frequency: Every 5 minutes (288 readings per day)")
        logger.info("Device: GARNI 925T weather station")
        logger.info("Location: Kozlovice")
        
        self.running = True
        self.stats['start_time'] = datetime.now()
        
        # Schedule data collection every 5 minutes
        schedule.every(5).minutes.do(self.collect_weather_data)
        
        # Initial collection
        self.collect_weather_data()
        
        # Start the scheduling thread
        self.collection_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.collection_thread.start()
        
        logger.info("🚀 Persistent weather service started successfully")
        logger.info("📊 Expected: 288 readings per day, 2016 per week")
        
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        return True
    
    def _run_scheduler(self):
        """Run the scheduler in a separate thread"""
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def stop_service(self):
        """Stop the persistent weather collection service"""
        
        logger.info("Stopping persistent weather service...")
        self.running = False
        
        # Clear scheduled jobs
        schedule.clear()
        
        # Update status file
        self.update_status_file()
        
        logger.info("Persistent weather service stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.stop_service()
        sys.exit(0)
    
    def get_status(self):
        """Get current service status"""
        
        return {
            'is_running': self.running,
            'stats': self.stats.copy(),
            'next_collection': datetime.now() + timedelta(minutes=5) if self.running else None
        }

def main():
    """Main function to run as standalone service"""
    
    service = PersistentWeatherService()
    
    try:
        service.start_service()
        
        # Keep the service running
        while service.running:
            time.sleep(60)
            
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Service error: {e}")
    finally:
        service.stop_service()

if __name__ == "__main__":
    main()