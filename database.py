"""Database operations for weather data storage and retrieval."""

import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Optional
from config import DATABASE_PATH

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherDatabase:
    """Handle all database operations for weather data."""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        """Initialize database connection and create tables if needed."""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create database tables if they don't exist."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Create weather_data table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS weather_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME NOT NULL,
                        source TEXT NOT NULL,
                        temperature REAL,
                        humidity REAL,
                        pressure REAL,
                        wind_speed REAL,
                        wind_direction REAL,
                        wind_gust REAL,
                        rainfall REAL,
                        uv_index REAL,
                        solar_radiation REAL,
                        dew_point REAL,
                        feels_like REAL,
                        air_quality_aqi INTEGER,
                        air_quality_pm25 REAL,
                        air_quality_pm10 REAL,
                        condition TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                
                # Create index for faster queries
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_timestamp 
                    ON weather_data(timestamp)
                """)
                
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_source 
                    ON weather_data(source)
                """)
                
                conn.commit()
                logger.info("Database initialized successfully")
                
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise
    
    def insert_weather_data(self, data: Dict) -> bool:
        """Insert weather data into the database."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    INSERT INTO weather_data (
                        timestamp, source, temperature, humidity, pressure,
                        wind_speed, wind_direction, wind_gust, rainfall,
                        uv_index, solar_radiation, dew_point, feels_like,
                        air_quality_aqi, air_quality_pm25, air_quality_pm10,
                        condition
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data.get('timestamp'),
                    data.get('source'),
                    data.get('temperature'),
                    data.get('humidity'),
                    data.get('pressure'),
                    data.get('wind_speed'),
                    data.get('wind_direction'),
                    data.get('wind_gust'),
                    data.get('rainfall'),
                    data.get('uv_index'),
                    data.get('solar_radiation'),
                    data.get('dew_point'),
                    data.get('feels_like'),
                    data.get('air_quality_aqi'),
                    data.get('air_quality_pm25'),
                    data.get('air_quality_pm10'),
                    data.get('condition')
                ))
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Error inserting weather data: {e}")
            return False
    
    def get_latest_data(self, limit: int = 1) -> pd.DataFrame:
        """Get the most recent weather data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM weather_data 
                    ORDER BY timestamp DESC 
                    LIMIT ?
                """
                return pd.read_sql_query(query, conn, params=(limit,))
        except Exception as e:
            logger.error(f"Error getting latest data: {e}")
            return pd.DataFrame()
    
    def get_data_by_date_range(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get weather data for a specific date range."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT * FROM weather_data 
                    WHERE timestamp BETWEEN ? AND ?
                    ORDER BY timestamp ASC
                """
                return pd.read_sql_query(
                    query, conn, 
                    params=(start_date.isoformat(), end_date.isoformat())
                )
        except Exception as e:
            logger.error(f"Error getting data by date range: {e}")
            return pd.DataFrame()
    
    def get_daily_aggregates(self, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        """Get daily aggregated weather data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                query = """
                    SELECT 
                        DATE(timestamp) as date,
                        AVG(temperature) as avg_temperature,
                        MIN(temperature) as min_temperature,
                        MAX(temperature) as max_temperature,
                        AVG(humidity) as avg_humidity,
                        AVG(pressure) as avg_pressure,
                        AVG(wind_speed) as avg_wind_speed,
                        MAX(wind_gust) as max_wind_gust,
                        SUM(rainfall) as total_rainfall,
                        AVG(uv_index) as avg_uv_index,
                        AVG(solar_radiation) as avg_solar_radiation,
                        COUNT(*) as record_count
                    FROM weather_data 
                    WHERE timestamp BETWEEN ? AND ?
                    GROUP BY DATE(timestamp)
                    ORDER BY date ASC
                """
                return pd.read_sql_query(
                    query, conn, 
                    params=(start_date.isoformat(), end_date.isoformat())
                )
        except Exception as e:
            logger.error(f"Error getting daily aggregates: {e}")
            return pd.DataFrame()
    
    def get_data_stats(self) -> Dict:
        """Get basic statistics about stored data."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total records
                cursor.execute("SELECT COUNT(*) FROM weather_data")
                total_records = cursor.fetchone()[0]
                
                # Date range
                cursor.execute("""
                    SELECT MIN(timestamp), MAX(timestamp) 
                    FROM weather_data
                """)
                date_range = cursor.fetchone()
                
                # Records by source
                cursor.execute("""
                    SELECT source, COUNT(*) 
                    FROM weather_data 
                    GROUP BY source
                """)
                sources = dict(cursor.fetchall())
                
                return {
                    'total_records': total_records,
                    'date_range': date_range,
                    'sources': sources
                }
        except Exception as e:
            logger.error(f"Error getting data stats: {e}")
            return {}
    
    def export_to_csv(self, start_date: datetime, end_date: datetime, 
                     filename: str) -> bool:
        """Export data to CSV file."""
        try:
            df = self.get_data_by_date_range(start_date, end_date)
            if not df.empty:
                df.to_csv(filename, index=False)
                logger.info(f"Data exported to {filename}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False
    
    def cleanup_old_data(self, days_to_keep: int = 365) -> bool:
        """Remove data older than specified days."""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    DELETE FROM weather_data 
                    WHERE timestamp < ?
                """, (cutoff_date.isoformat(),))
                deleted_count = cursor.rowcount
                conn.commit()
                logger.info(f"Cleaned up {deleted_count} old records")
                return True
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}")
            return False
