#!/usr/bin/env python3
"""
Automatic weather data collection service
Collects GARNI 925T data every 5 minutes (288 readings per day)
"""

import time
import threading
import schedule
from datetime import datetime, timedelta
from data_collector import WeatherDataCollector
from database import WeatherDatabase
import logging
from timezone_utils import now_prague, format_prague_time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AutoCollectorService:
    """Automatic weather data collection service"""
    
    def __init__(self):
        self.collector = WeatherDataCollector()
        self.db = WeatherDatabase()
        self.is_running = False
        self.collection_thread = None
        self.stats = {
            'total_collections': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'last_collection': None,
            'last_success': None
        }
    
    def collect_weather_data(self):
        """Collect weather data with error handling and stats tracking"""
        try:
            logger.info("Starting automatic weather data collection...")
            
            # Collect data
            success = self.collector.collect_tuya_data()
            
            self.stats['total_collections'] += 1
            self.stats['last_collection'] = now_prague()
            
            if success:
                self.stats['successful_collections'] += 1
                self.stats['last_success'] = now_prague()
                
                # Log collection success with current readings
                latest = self.db.get_latest_data()
                if not latest.empty:
                    latest_record = latest.iloc[0]
                    temp = latest_record.get('temperature')
                    humid = latest_record.get('humidity')
                    pressure = latest_record.get('pressure')
                    
                    params = []
                    if temp is not None:
                        params.append(f"T={temp:.1f}°C")
                    if humid is not None:
                        params.append(f"H={humid:.0f}%")
                    if pressure is not None:
                        params.append(f"P={pressure:.1f}hPa")
                    
                    logger.info(f"✅ Collection successful: {', '.join(params) if params else 'Data collected'}")
                else:
                    logger.info("✅ Collection successful")
            else:
                self.stats['failed_collections'] += 1
                logger.warning("❌ Collection failed")
                
        except Exception as e:
            self.stats['failed_collections'] += 1
            logger.error(f"❌ Collection error: {e}")
    
    def start_automatic_collection(self):
        """Start automatic collection every 5 minutes"""
        if self.is_running:
            logger.warning("Auto-collection already running")
            return
        
        logger.info("=== STARTING AUTOMATIC WEATHER DATA COLLECTION ===")
        logger.info("Collection frequency: Every 5 minutes (288 readings per day)")
        logger.info("Device: GARNI 925T weather station")
        logger.info("Location: Kozlovice")
        
        # Schedule collection every 5 minutes
        schedule.every(5).minutes.do(self.collect_weather_data)
        
        # Collect immediately on start
        self.collect_weather_data()
        
        self.is_running = True
        
        # Start scheduler in separate thread
        def run_scheduler():
            while self.is_running:
                schedule.run_pending()
                time.sleep(30)  # Check every 30 seconds
        
        self.collection_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.collection_thread.start()
        
        logger.info("🚀 Automatic collection started successfully")
        logger.info("📊 Expected: 288 readings per day, 2016 per week")
    
    def stop_automatic_collection(self):
        """Stop automatic collection"""
        if not self.is_running:
            logger.warning("Auto-collection not running")
            return
        
        self.is_running = False
        schedule.clear()
        
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        logger.info("🛑 Automatic collection stopped")
    
    def get_collection_status(self):
        """Get current collection status and statistics"""
        status = {
            'is_running': self.is_running,
            'stats': self.stats.copy(),
            'next_collection': None
        }
        
        if self.is_running and schedule.jobs:
            next_job = schedule.next_run()
            if next_job:
                status['next_collection'] = next_job
        
        return status
    
    def get_daily_collection_stats(self, days=7):
        """Get daily collection statistics for the last N days"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            df = self.db.get_data_by_date_range(start_date, end_date)
            
            if df.empty:
                return {}
            
            # Filter GARNI data
            garni_df = df[df['source'].str.contains('garni_925t')]
            
            if garni_df.empty:
                return {}
            
            import pandas as pd
            garni_df['timestamp'] = pd.to_datetime(garni_df['timestamp'])
            garni_df['date'] = garni_df['timestamp'].dt.date
            
            # Daily counts
            daily_counts = garni_df.groupby('date').size()
            
            stats = {
                'total_readings': len(garni_df),
                'daily_average': daily_counts.mean(),
                'best_day': daily_counts.max(),
                'worst_day': daily_counts.min(),
                'daily_counts': daily_counts.to_dict()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting daily stats: {e}")
            return {}

# Global service instance
auto_collector = AutoCollectorService()

def start_service():
    """Start the automatic collection service"""
    auto_collector.start_automatic_collection()

def stop_service():
    """Stop the automatic collection service"""
    auto_collector.stop_automatic_collection()

def get_status():
    """Get service status"""
    return auto_collector.get_collection_status()

def get_daily_stats(days=7):
    """Get daily collection statistics"""
    return auto_collector.get_daily_collection_stats(days)

if __name__ == "__main__":
    # Start service when run directly
    try:
        start_service()
        
        # Keep running
        while True:
            time.sleep(60)
            
            # Log status every hour
            if datetime.now().minute == 0:
                status = get_status()
                stats = status['stats']
                success_rate = (stats['successful_collections'] / max(stats['total_collections'], 1)) * 100
                logger.info(f"📊 Status: {stats['total_collections']} total, {success_rate:.1f}% success rate")
                
    except KeyboardInterrupt:
        logger.info("Stopping automatic collection service...")
        stop_service()