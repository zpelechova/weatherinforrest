# Weather Monitoring Platform

## Overview

This is a comprehensive weather monitoring platform built with Streamlit that collects, stores, analyzes, and visualizes weather data from multiple sources. The application integrates with Tuya-based weather stations (specifically GARNI 925T) and external weather APIs to provide real-time monitoring and historical analysis capabilities.

## User Preferences

Preferred communication style: Simple, everyday language.

**Development Approach**: Iterative deployment and data-driven design
- Deploy early for production data collection
- Collect substantial dataset first, then revisit dashboard design
- Focus on data accumulation before optimizing visualization
- Preference for building comprehensive dataset, then customizing displays based on actual data patterns

**Data Collection Priority**: Automated comprehensive collection (288 readings/day) taking precedence over historical data import
- Automatic collection every 5 minutes established as primary data source
- Historical data import secondary priority
- Focus on building substantial future dataset for analysis

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface for data visualization and user interaction
- **Data Collection**: Automated collection system with scheduling capabilities
- **Data Storage**: SQLite database for local data persistence
- **Analysis Engine**: Weather data analysis and trend calculation
- **External Integrations**: Tuya API for weather station data and Meteostat for historical weather data

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Primary Streamlit interface and application orchestration
- **Features**: Dashboard visualization, configuration management, data display
- **Architecture Decision**: Uses Streamlit for rapid prototyping and easy deployment, with session state management for persistent UI state

### 2. Database Layer (`database.py`)
- **Purpose**: Data persistence and retrieval operations
- **Technology**: SQLite database
- **Schema**: Single `weather_data` table with comprehensive weather parameters
- **Architecture Decision**: SQLite chosen for simplicity and local deployment, avoiding need for external database server

### 3. Data Collection System (`data_collector.py`)
- **Purpose**: Automated data collection from multiple sources
- **Features**: Scheduled collection, threading support, multiple data source integration
- **Architecture Decision**: Uses threading and scheduling to run collection independently from the main UI

### 4. Tuya Integration (`tuya_client.py`)
- **Purpose**: Interface with Tuya Cloud API for weather station data
- **Features**: API authentication, device status retrieval, signature generation
- **Architecture Decision**: Direct API integration chosen over local device communication for cloud-based access

### 5. Analysis Engine (`weather_analysis.py`)
- **Purpose**: Weather data analysis and visualization generation
- **Features**: Trend calculation, statistical analysis, chart generation
- **Technology**: Pandas for data manipulation, Plotly for interactive visualizations

### 6. Configuration Management (`config.py`)
- **Purpose**: Centralized configuration using environment variables
- **Features**: API credentials, database paths, collection intervals
- **Architecture Decision**: Environment-based configuration for security and deployment flexibility

## Data Flow

1. **Collection**: Automated collectors fetch data from Tuya API and Meteostat
2. **Storage**: Raw data stored in SQLite with timestamps and source identification
3. **Processing**: Data retrieved and processed for analysis using Pandas
4. **Visualization**: Processed data rendered using Plotly charts in Streamlit interface
5. **User Interaction**: Users can filter, analyze, and export data through the web interface

## External Dependencies

### Required Services
- **Tuya Cloud API**: For weather station device data
- **Meteostat API**: For historical weather data (optional)

### Key Libraries
- **Streamlit**: Web interface framework
- **Pandas**: Data manipulation and analysis
- **Plotly**: Interactive data visualization
- **SQLite3**: Database operations
- **Requests**: HTTP API communication
- **Schedule**: Task scheduling for data collection

## Deployment Strategy

The application is designed for local deployment with the following characteristics:

- **Database**: Local SQLite file for data persistence
- **Configuration**: Environment variables for sensitive credentials
- **Scheduling**: In-process threading for automated data collection
- **Web Interface**: Streamlit development server for local access

### Environment Variables Required
- `TUYA_ACCESS_ID`: Tuya API access identifier
- `TUYA_ACCESS_KEY`: Tuya API secret key
- `TUYA_DEVICE_ID`: Weather station device identifier
- `STATION_LATITUDE`: Geographic latitude for location-based data
- `STATION_LONGITUDE`: Geographic longitude for location-based data

### Deployment Considerations
- Single-user deployment model
- No external database server required
- Minimal infrastructure requirements
- Suitable for personal weather monitoring or small-scale applications

The architecture prioritizes simplicity and ease of deployment while maintaining modularity for future enhancements and scalability.

## Recent Changes and Status (August 2025)

### Data Collection System Status
- **Automatic Collection**: Active and deployed, collecting every 5 minutes (288 readings/day)
- **Current Data**: Building comprehensive dataset from GARNI 925T weather station
- **Location**: Kozlovice (corrected from Prague in all system components)
- **Parameters**: Temperature, humidity, pressure, wind speed, UV index

### Deployment Strategy
- **Current Status**: Deployed for production data collection
- **Data-First Approach**: Accumulate substantial dataset before dashboard redesign
- **Future Enhancement**: Dashboard visualization and analysis features to be revisited after sufficient data collection

### Known Limitations Addressed
- **Tuya API Trial**: Limited historical data access (sparse readings vs comprehensive logs)
- **Smart Life Export**: Manual export process required for historical data import
- **Solution Implemented**: Robust automatic collection system compensates for API limitations

The system follows user preference for iterative deployment: deploy early for data collection, then enhance visualization based on accumulated real-world data patterns.

## Monitoring and Review Schedule

### Automated Monitoring (August 2025)
- **Hourly Checks**: Automated verification of weather data collection (12 readings/hour expected)
- **Daily Summaries**: Collection statistics and weather range reports
- **Alert System**: Notifications for collection failures or service issues
- **Log Files**: Detailed monitoring history for troubleshooting

### Scheduled Review
- **Three Day Review**: August 5, 2025 - Assess data collection performance and plan dashboard enhancements
- **Data Target**: 864+ comprehensive readings over 3 days (288/day)
- **Goal**: Use accumulated real-world data to inform dashboard customization priorities