"""Simple Weather Monitoring Dashboard - Guaranteed to work"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from database import WeatherDatabase
from data_collector import WeatherDataCollector
from config import STATION_LATITUDE, STATION_LONGITUDE
from timezone_utils import now_prague, format_prague_time

# Page configuration
st.set_page_config(
    page_title="Weather Monitoring Platform",
    page_icon="🌤️",
    layout="wide"
)

st.title("🌤️ Weather Monitoring Platform")
st.markdown("**GARNI 925T Smart Weather Station - Kozlovice**")

# Initialize database
db = WeatherDatabase()

# Sidebar controls
st.sidebar.title("🔧 Control Panel")

# Auto-collection status
try:
    from auto_collector_service import get_status, start_service, stop_service
    
    status = get_status()
    
    if status['is_running']:
        st.sidebar.success("✅ Auto-collection: ACTIVE")
        if st.sidebar.button("⏹️ Stop Collection"):
            stop_service()
            st.rerun()
        
        stats = status['stats']
        if stats['total_collections'] > 0:
            success_rate = (stats['successful_collections'] / stats['total_collections']) * 100
            st.sidebar.metric("Success Rate", f"{success_rate:.1f}%")
    else:
        st.sidebar.warning("⏸️ Auto-collection: STOPPED")
        if st.sidebar.button("▶️ Start Collection"):
            start_service()
            st.rerun()

except Exception as e:
    st.sidebar.error(f"Collection service: {e}")

# Manual collection
if st.sidebar.button("📥 Collect Now"):
    try:
        collector = WeatherDataCollector()
        success = collector.collect_tuya_data()
        
        if success:
            st.sidebar.success("✅ Data collected!")
        else:
            st.sidebar.error("❌ Collection failed")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"Error: {e}")

# Location info
st.sidebar.info(f"📍 Location: Kozlovice\n({STATION_LATITUDE:.4f}, {STATION_LONGITUDE:.4f})")

# Main content
col1, col2, col3 = st.columns(3)

# Current conditions
latest_data = db.get_latest_data(limit=1)

if not latest_data.empty:
    latest = latest_data.iloc[0]
    
    with col1:
        if 'temperature' in latest and pd.notna(latest['temperature']):
            st.metric("Temperature", f"{latest['temperature']:.1f}°C")
        
    with col2:
        if 'humidity' in latest and pd.notna(latest['humidity']):
            st.metric("Humidity", f"{latest['humidity']:.0f}%")
    
    with col3:
        if 'pressure' in latest and pd.notna(latest['pressure']):
            st.metric("Pressure", f"{latest['pressure']:.1f} hPa")
    
    # Last update time
    if 'timestamp' in latest and pd.notna(latest['timestamp']):
        update_time = latest['timestamp']
        if isinstance(update_time, str):
            update_time = pd.to_datetime(update_time)
        st.info(f"Last update: {format_prague_time(update_time)} (Prague time)")
else:
    st.warning("No weather data available. Start data collection to see current conditions.")

# Recent data table
st.subheader("📊 Recent Weather Data")

# Get last 24 hours of data
end_time = datetime.now()
start_time = end_time - timedelta(hours=24)
recent_data = db.get_data_by_date_range(start_time, end_time)

if not recent_data.empty:
    # Filter for GARNI data
    garni_data = recent_data[recent_data['source'].str.contains('garni', case=False, na=False)]
    
    if not garni_data.empty:
        st.success(f"Showing {len(garni_data)} readings from last 24 hours")
        
        # Display recent readings
        display_data = garni_data[['timestamp', 'temperature', 'humidity', 'pressure']].tail(10)
        st.dataframe(display_data, use_container_width=True)
        
        # Simple statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if 'temperature' in garni_data.columns:
                temp_data = garni_data['temperature'].dropna()
                if len(temp_data) > 0:
                    st.metric("Temp Range", f"{temp_data.min():.1f}°C - {temp_data.max():.1f}°C")
        
        with col2:
            if 'humidity' in garni_data.columns:
                humid_data = garni_data['humidity'].dropna()
                if len(humid_data) > 0:
                    st.metric("Humidity Range", f"{humid_data.min():.0f}% - {humid_data.max():.0f}%")
        
        with col3:
            st.metric("Total Readings", len(garni_data))
    else:
        st.info("No GARNI weather station data found in the last 24 hours.")
else:
    st.info("No recent weather data found. Data collection may be starting up.")

# Export functionality
st.subheader("💾 Export Data")

if st.button("📤 Export Recent Data as CSV"):
    if not recent_data.empty:
        csv_data = recent_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv_data,
            file_name=f"weather_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available for export")

# System status
with st.expander("🔍 System Status"):
    st.markdown(f"""
    **Database Status:** Connected
    **Location:** Kozlovice ({STATION_LATITUDE:.4f}, {STATION_LONGITUDE:.4f})
    **Device:** GARNI 925T Smart Weather Station
    **Collection:** Every 5 minutes (288 readings/day target)
    **Current Time:** {format_prague_time(now_prague())} (Prague time)
    """)