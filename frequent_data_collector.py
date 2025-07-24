#!/usr/bin/env python3
"""
Frequent data collection from GARNI 925T to build comprehensive historical dataset
Since API doesn't provide historical logs, collect frequently going forward
"""

import time
import schedule
from datetime import datetime
from data_collector import WeatherDataCollector
from database import WeatherDatabase

class FrequentDataCollector:
    """Collect data every 5 minutes to build comprehensive dataset"""
    
    def __init__(self):
        self.collector = WeatherDataCollector()
        self.db = WeatherDatabase()
    
    def collect_now(self):
        """Collect data immediately with detailed logging"""
        try:
            print(f"🔄 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting GARNI 925T data...")
            success = self.collector.collect_tuya_data()
            
            if success:
                # Get latest record to show what was collected
                latest = self.db.get_latest_data()
                if not latest.empty:
                    latest_record = latest.iloc[0]
                    params = []
                    if latest_record.get('temperature') is not None:
                        params.append(f"T={latest_record['temperature']:.1f}°C")
                    if latest_record.get('humidity') is not None:
                        params.append(f"H={latest_record['humidity']:.0f}%")
                    if latest_record.get('pressure') is not None:
                        params.append(f"P={latest_record['pressure']:.1f}hPa")
                    
                    print(f"✅ Collected: {', '.join(params) if params else 'No parameters'}")
                else:
                    print("✅ Data collected (no details available)")
            else:
                print("❌ Collection failed")
                
        except Exception as e:
            print(f"❌ Collection error: {e}")
    
    def start_frequent_collection(self):
        """Start collecting data every 5 minutes"""
        
        print("=== STARTING FREQUENT GARNI 925T DATA COLLECTION ===")
        print("Collecting every 5 minutes to build comprehensive historical dataset")
        print("This compensates for lack of API historical access")
        print()
        
        # Schedule collection every 5 minutes
        schedule.every(5).minutes.do(self.collect_now)
        
        # Also collect immediately
        self.collect_now()
        
        print(f"⏰ Scheduled collection every 5 minutes")
        print(f"📊 This will create 288 readings per day (24x12)")
        print(f"🗓️  In 30 days: ~8,640 comprehensive readings")
        print()
        print("Press Ctrl+C to stop")
        
        # Run scheduler
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Stopping frequent collection")

    def show_collection_stats(self):
        """Show current collection statistics"""
        
        from datetime import timedelta
        
        print("=== COLLECTION STATISTICS ===")
        
        # Get total GARNI data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        df = self.db.get_data_by_date_range(start_date, end_date)
        
        if not df.empty:
            garni_df = df[df['source'].str.contains('garni_925t')]
            
            if not garni_df.empty:
                import pandas as pd
                garni_df['timestamp'] = pd.to_datetime(garni_df['timestamp'])
                
                # Daily counts
                garni_df['date'] = garni_df['timestamp'].dt.date
                daily_counts = garni_df.groupby('date').size()
                
                print(f"📊 Total GARNI readings: {len(garni_df)}")
                print(f"📅 Date range: {garni_df['timestamp'].min()} to {garni_df['timestamp'].max()}")
                print(f"📈 Average per day: {daily_counts.mean():.1f}")
                print(f"📊 Best day: {daily_counts.max()} readings")
                print()
                
                print("📋 Recent daily counts:")
                for date, count in daily_counts.tail(10).items():
                    print(f"   {date}: {count} readings")
            else:
                print("No GARNI data found")
        else:
            print("No data found")

if __name__ == "__main__":
    collector = FrequentDataCollector()
    
    # Show current stats
    collector.show_collection_stats()
    
    print()
    print("🚀 Ready to start frequent collection")
    print("This will create comprehensive historical data going forward")
    
    # Ask user what to do
    action = input("\nChoose action:\n1. Start frequent collection (5 min intervals)\n2. Collect once now\n3. Show stats only\nEnter 1, 2, or 3: ")
    
    if action == "1":
        collector.start_frequent_collection()
    elif action == "2":
        collector.collect_now()
    elif action == "3":
        print("Stats shown above")
    else:
        print("Invalid choice")