"""Configuration settings for the weather monitoring platform."""

import os

# Tuya API Configuration
TUYA_ACCESS_ID = os.getenv("TUYA_ACCESS_ID", "")
TUYA_ACCESS_KEY = os.getenv("TUYA_ACCESS_KEY", "")
TUYA_API_ENDPOINT = os.getenv("TUYA_API_ENDPOINT", "https://openapi.tuyacn.com")
TUYA_DEVICE_ID = os.getenv("TUYA_DEVICE_ID", "")

# Database Configuration
DATABASE_PATH = "weather_data.db"

# Data Collection Configuration
COLLECTION_INTERVAL_MINUTES = 15  # Collect data every 15 minutes
BACKUP_INTERVAL_HOURS = 24  # Backup data every 24 hours

# Weather Station Location (for Meteostat API)
STATION_LATITUDE = float(os.getenv("STATION_LATITUDE", "50.0"))
STATION_LONGITUDE = float(os.getenv("STATION_LONGITUDE", "14.0"))

# API Configuration
MAX_RETRIES = 3
REQUEST_TIMEOUT = 30

# Chart Configuration
DEFAULT_CHART_HEIGHT = 400
DEFAULT_DATE_RANGE_DAYS = 7
