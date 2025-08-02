# Weather Monitoring Platform

A comprehensive weather monitoring and analysis system for GARNI 925T SMART weather station using Tuya IoT platform integration.

## Overview

This platform provides real-time weather data collection, historical analysis, and visualization for the GARNI 925T weather station located in Kozlovice. The system collects data every 5 minutes (288 readings per day) and displays all information in Prague timezone.

## Features

- **Real-time Data Collection**: Automated collection every 5 minutes from GARNI 925T weather station
- **Prague Timezone**: All timestamps displayed in Central European Time (CET/CEST)
- **Comprehensive Monitoring**: Temperature, humidity, pressure, wind speed, UV index
- **Interactive Dashboard**: Streamlit-based web interface with charts and analytics
- **Data Export**: CSV and Excel export capabilities
- **Historical Analysis**: Trend analysis and statistical insights
- **Redundant Collection**: Multiple collection services for reliability

## Technical Architecture

### Core Components

- **Frontend**: Streamlit web application (`app.py`)
- **Data Collection**: Automated collection service (`auto_collector_service.py`)
- **Database**: SQLite for local data persistence (`database.py`)
- **API Integration**: Tuya Cloud API client (`tuya_client.py`)
- **Timezone Support**: Prague/CET timezone utilities (`timezone_utils.py`)
- **Backup Service**: Persistent collection service (`persistent_weather_service.py`)

### Data Flow

1. **Collection**: Tuya API → Data Collector → SQLite Database
2. **Processing**: Database → Pandas → Analysis Engine
3. **Visualization**: Processed Data → Plotly Charts → Streamlit Interface
4. **Export**: Database → CSV/Excel files

## Installation

### Prerequisites

- Python 3.11+
- Tuya IoT Cloud account with device credentials
- GARNI 925T weather station linked to Tuya Smart Life app

### Dependencies

```bash
pip install streamlit pandas plotly requests schedule pytz tinytuya meteostat
```

### Environment Variables

Required environment variables:

```bash
TUYA_ACCESS_ID=your_tuya_access_id
TUYA_ACCESS_KEY=your_tuya_access_key
TUYA_DEVICE_ID=your_device_id
STATION_LATITUDE=50.4489643
STATION_LONGITUDE=14.3095035
```

## Usage

### Start the Application

```bash
streamlit run app.py --server.port 5000
```

### Access the Dashboard

- Main Interface: `http://localhost:5000`
- Simple View: `http://localhost:5001` (via `simple_app.py`)

### Data Collection

The system automatically starts data collection when the application loads:

- **Collection Frequency**: Every 5 minutes
- **Expected Daily Readings**: 288
- **Auto-restart**: Service automatically restarts if stopped
- **Backup Service**: Independent persistent collection service

## Configuration

### Timezone Settings

All times display in Prague timezone (Europe/Prague):
- Automatic daylight saving time handling
- CET (UTC+1) in winter, CEST (UTC+2) in summer
- Collection schedules and timestamps in local time

### Collection Settings

- **Interval**: 5 minutes (configurable)
- **Target**: 288 readings per day
- **Retry Logic**: Automatic retry on failures
- **Error Handling**: Comprehensive logging and recovery

## Deployment

### Local Development

```bash
git clone [repository-url]
cd weather-monitoring-platform
pip install -r requirements.txt
streamlit run app.py
```

### Production Deployment

The system is designed for Replit deployment with:
- Automatic workflow management
- Environment variable configuration
- Reserved VM for continuous operation
- Custom domain support (weatherinforrest.replit.app)

## Data Structure

### Weather Data Schema

```sql
CREATE TABLE weather_data (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME NOT NULL,
    source TEXT NOT NULL,
    temperature REAL,
    humidity REAL,
    pressure REAL,
    wind_speed REAL,
    wind_direction REAL,
    uv_index REAL,
    -- Additional parameters...
);
```

### Data Sources

- **Primary**: GARNI 925T via Tuya API (every 5 minutes)
- **Backup**: Device memory extraction (sparse historical data)
- **Import**: Smart Life app exports (CSV/Excel)

## Monitoring

### Automatic Monitoring

- **Hourly Checks**: Collection status verification
- **Daily Reports**: Statistics and performance metrics
- **Alert System**: Failure notifications and auto-recovery
- **Log Files**: Detailed operation history

### Status Indicators

- **Auto-collection Status**: ACTIVE/STOPPED with auto-restart
- **Success Rate**: Percentage of successful collections
- **Next Collection**: Prague time for next scheduled collection
- **Data Quality**: Validation and completeness checks

## API Integration

### Tuya IoT Platform

- **API Version**: Tuya Cloud API v1.0
- **Authentication**: OAuth 2.0 with access tokens
- **Rate Limits**: Optimized for 5-minute intervals
- **Error Handling**: Retry logic and fallback strategies

### Device Support

- **Primary Device**: GARNI 925T Smart Weather Station
- **Compatibility**: Tuya-compatible weather stations
- **Parameters**: Temperature, humidity, pressure, wind, UV index

## Contributing

### Development Guidelines

1. **Code Style**: Follow PEP 8 standards
2. **Documentation**: Update README.md for major changes
3. **Testing**: Test with real weather station data
4. **Timezone**: Always use Prague timezone utilities
5. **Error Handling**: Implement comprehensive error recovery

### Architecture Updates

When making architectural changes:
1. Update `replit.md` with technical details
2. Document in README.md for users
3. Update deployment configuration
4. Test with production data

## License

This project is designed for personal weather monitoring and educational purposes.

## Support

For issues with:
- **Tuya API**: Check device credentials and API limits
- **Data Collection**: Review logs and service status
- **Deployment**: Ensure environment variables are set
- **Timezone**: Verify Prague timezone configuration

## Project Status

**Current Version**: Production deployment with automatic data collection
**Data Collection**: Active since August 2025
**Location**: Kozlovice, Czech Republic
**Timezone**: Europe/Prague (CET/CEST)
**Collection Target**: 288 readings per day