"""Main Streamlit application for weather monitoring and analysis platform."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging
import os
from io import BytesIO

# Import custom modules
from database import WeatherDatabase
from data_collector import get_collector
from tuya_client import TuyaWeatherClient
from weather_analysis import (
    WeatherAnalyzer, create_time_series_chart, create_correlation_heatmap,
    create_daily_pattern_chart, create_summary_dashboard
)
from config import (
    TUYA_ACCESS_ID, TUYA_ACCESS_KEY, STATION_LATITUDE, STATION_LONGITUDE,
    DEFAULT_DATE_RANGE_DAYS
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Weather Monitoring Platform",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'data_collector_started' not in st.session_state:
    st.session_state.data_collector_started = False

def check_configuration():
    """Check if required configuration is available."""
    config_status = {
        "tuya_configured": bool(TUYA_ACCESS_ID and TUYA_ACCESS_KEY),
        "location_configured": bool(STATION_LATITUDE and STATION_LONGITUDE),
    }
    return config_status

def display_configuration_status():
    """Display configuration status in sidebar."""
    st.sidebar.subheader("📋 Configuration Status")
    
    config = check_configuration()
    
    if config["tuya_configured"]:
        st.sidebar.success("✅ Tuya API Configured")
    else:
        st.sidebar.error("❌ Tuya API Not Configured")
        st.sidebar.info("Set TUYA_ACCESS_ID and TUYA_ACCESS_KEY environment variables")
    
    if config["location_configured"]:
        st.sidebar.success(f"✅ Location: {STATION_LATITUDE:.2f}, {STATION_LONGITUDE:.2f}")
    else:
        st.sidebar.error("❌ Location Not Configured")
        st.sidebar.info("Set STATION_LATITUDE and STATION_LONGITUDE environment variables")
    
    return all(config.values())

def display_data_collection_controls():
    """Display data collection controls in sidebar."""
    st.sidebar.subheader("🔄 Data Collection")
    
    collector = get_collector()
    status = collector.get_collection_status()
    
    if status["is_running"]:
        st.sidebar.success("✅ Collection Running")
        if st.sidebar.button("Stop Collection"):
            collector.stop_scheduled_collection()
            st.session_state.data_collector_started = False
            st.rerun()
    else:
        st.sidebar.warning("⏸️ Collection Stopped")
        if st.sidebar.button("Start Collection"):
            collector.start_scheduled_collection()
            st.session_state.data_collector_started = True
            st.rerun()
    
    # Manual collection button
    if st.sidebar.button("📥 Collect Now"):
        with st.sidebar:
            with st.spinner("Collecting data..."):
                collector.run_collection_cycle()
        st.sidebar.success("Data collection completed!")
        st.rerun()
    
    # Historical data collection
    st.sidebar.subheader("📚 Historical Data")
    days_back = st.sidebar.selectbox("Collect Historical Data", [7, 30, 90, 365])
    
    if st.sidebar.button("Download Historical Data"):
        with st.sidebar:
            with st.spinner(f"Collecting {days_back} days of historical data..."):
                success = collector.collect_historical_data(days_back)
        if success:
            st.sidebar.success(f"✅ Historical data collected ({days_back} days)")
        else:
            st.sidebar.error("❌ Failed to collect historical data")
        st.rerun()
    
    return status

def display_current_conditions():
    """Display current weather conditions."""
    st.header("🌤️ Current Conditions")
    
    db = WeatherDatabase()
    latest_data = db.get_latest_data(limit=1)
    
    if latest_data.empty:
        st.warning("No current weather data available. Start data collection to see live conditions.")
        return
    
    latest = latest_data.iloc[0]
    
    # Create columns for metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if pd.notna(latest.get('temperature')):
            st.metric(
                label="Temperature",
                value=f"{latest['temperature']:.1f}°C",
                delta=None
            )
        
        if pd.notna(latest.get('humidity')):
            st.metric(
                label="Humidity", 
                value=f"{latest['humidity']:.1f}%"
            )
    
    with col2:
        if pd.notna(latest.get('pressure')):
            st.metric(
                label="Pressure",
                value=f"{latest['pressure']:.1f} hPa"
            )
        
        if pd.notna(latest.get('wind_speed')):
            st.metric(
                label="Wind Speed",
                value=f"{latest['wind_speed']:.1f} m/s"
            )
    
    with col3:
        if pd.notna(latest.get('uv_index')):
            st.metric(
                label="UV Index",
                value=f"{latest['uv_index']:.1f}"
            )
        
        if pd.notna(latest.get('rainfall')):
            st.metric(
                label="Rainfall",
                value=f"{latest['rainfall']:.1f} mm"
            )
    
    with col4:
        if pd.notna(latest.get('air_quality_aqi')):
            st.metric(
                label="Air Quality (AQI)",
                value=f"{latest['air_quality_aqi']}"
            )
        
        st.info(f"Last updated: {latest['timestamp']}")
        st.info(f"Data source: {latest['source']}")

def display_time_series_analysis():
    """Display time-series analysis and charts."""
    st.header("📈 Time Series Analysis")
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=datetime.now().date() - timedelta(days=DEFAULT_DATE_RANGE_DAYS)
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=datetime.now().date()
        )
    
    # Get data for selected range
    db = WeatherDatabase()
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    df = db.get_data_by_date_range(start_datetime, end_datetime)
    
    if df.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Parameter selection
    available_params = [col for col in df.columns if col not in ['id', 'timestamp', 'source', 'created_at', 'condition']]
    available_params = [param for param in available_params if df[param].notna().any()]
    
    if not available_params:
        st.warning("No numeric weather parameters available.")
        return
    
    selected_param = st.selectbox("Select Parameter", available_params, index=0)
    
    # Create time series chart
    if selected_param:
        fig = create_time_series_chart(
            df, selected_param, 
            f"{selected_param.replace('_', ' ').title()} Over Time"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Display statistics
        analyzer = WeatherAnalyzer(df)
        trends = analyzer.calculate_trends(selected_param)
        
        if trends:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Current", f"{trends.get('current_value', 'N/A')}")
            with col2:
                st.metric("Average", f"{trends.get('mean', 0):.2f}")
            with col3:
                st.metric("Min/Max", f"{trends.get('min', 0):.1f} / {trends.get('max', 0):.1f}")
            with col4:
                trend_dir = trends.get('trend_direction', 'unknown')
                trend_emoji = {"increasing": "📈", "decreasing": "📉", "stable": "➡️"}.get(trend_dir, "❓")
                st.metric("Trend", f"{trend_emoji} {trend_dir.title()}")

def display_dashboard_overview():
    """Display comprehensive dashboard overview."""
    st.header("📊 Dashboard Overview")
    
    # Get recent data
    db = WeatherDatabase()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)  # Last 7 days
    
    df = db.get_data_by_date_range(start_date, end_date)
    
    if df.empty:
        st.warning("No data available for dashboard. Start data collection to view dashboard.")
        return
    
    # Create summary dashboard
    fig = create_summary_dashboard(df)
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data statistics
    st.subheader("📈 Data Statistics")
    
    stats = db.get_data_stats()
    if stats:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", stats.get('total_records', 0))
        
        with col2:
            date_range = stats.get('date_range', [None, None])
            if date_range[0] and date_range[1]:
                start_str = date_range[0][:10]  # Just the date part
                end_str = date_range[1][:10]
                st.metric("Date Range", f"{start_str} to {end_str}")
        
        with col3:
            sources = stats.get('sources', {})
            if sources:
                primary_source = max(sources.keys(), key=lambda k: sources[k])
                st.metric("Primary Source", f"{primary_source} ({sources[primary_source]} records)")

def display_trend_analysis():
    """Display trend analysis and patterns."""
    st.header("📊 Trend Analysis")
    
    # Get data for analysis
    db = WeatherDatabase()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)  # Last 30 days
    
    df = db.get_data_by_date_range(start_date, end_date)
    
    if df.empty:
        st.warning("No data available for trend analysis.")
        return
    
    analyzer = WeatherAnalyzer(df)
    
    # Parameter selection for analysis
    available_params = [col for col in df.columns if col not in ['id', 'timestamp', 'source', 'created_at', 'condition']]
    available_params = [param for param in available_params if df[param].notna().any()]
    
    if not available_params:
        st.warning("No numeric parameters available for analysis.")
        return
    
    selected_param = st.selectbox("Select Parameter for Analysis", available_params, key="trend_param")
    
    if selected_param:
        # Daily pattern analysis
        st.subheader(f"Daily Pattern - {selected_param.replace('_', ' ').title()}")
        daily_fig = create_daily_pattern_chart(df, selected_param)
        st.plotly_chart(daily_fig, use_container_width=True)
        
        # Pattern statistics
        patterns = analyzer.get_daily_patterns(selected_param)
        if patterns:
            col1, col2, col3 = st.columns(3)
            with col1:
                peak_hour = patterns.get('peak_hour', 'N/A')
                st.metric("Peak Hour", f"{peak_hour}:00" if peak_hour != 'N/A' else 'N/A')
            with col2:
                low_hour = patterns.get('low_hour', 'N/A')
                st.metric("Low Hour", f"{low_hour}:00" if low_hour != 'N/A' else 'N/A')
            with col3:
                daily_range = patterns.get('daily_range', 0)
                st.metric("Daily Range", f"{daily_range:.2f}")
        
        # Anomaly detection
        st.subheader("🚨 Anomaly Detection")
        anomalies = analyzer.detect_anomalies(selected_param)
        
        if anomalies:
            st.warning(f"Found {len(anomalies)} anomalies in the last 30 days:")
            
            # Display recent anomalies
            anomaly_df = pd.DataFrame(anomalies)
            anomaly_df['timestamp'] = pd.to_datetime(anomaly_df['timestamp'])
            recent_anomalies = anomaly_df.sort_values('timestamp').tail(5)
            
            for _, anomaly in recent_anomalies.iterrows():
                severity_emoji = "🔴" if anomaly['severity'] == 'high' else "🟡"
                st.write(f"{severity_emoji} **{anomaly['timestamp'].strftime('%Y-%m-%d %H:%M')}**: "
                        f"{anomaly['value']:.2f} (z-score: {anomaly['z_score']:.2f})")
        else:
            st.success("No anomalies detected in the selected parameter.")

def display_correlation_analysis():
    """Display correlation analysis between weather parameters."""
    st.header("🔗 Correlation Analysis")
    
    # Get data
    db = WeatherDatabase()
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    df = db.get_data_by_date_range(start_date, end_date)
    
    if df.empty:
        st.warning("No data available for correlation analysis.")
        return
    
    # Available parameters
    numeric_params = [col for col in df.columns if col not in ['id', 'timestamp', 'source', 'created_at', 'condition']]
    numeric_params = [param for param in numeric_params if df[param].notna().any()]
    
    if len(numeric_params) < 2:
        st.warning("Need at least 2 parameters for correlation analysis.")
        return
    
    # Create correlation heatmap
    fig = create_correlation_heatmap(df, numeric_params)
    st.plotly_chart(fig, use_container_width=True)
    
    # Calculate and display correlations
    analyzer = WeatherAnalyzer(df)
    correlations = analyzer.calculate_correlations(numeric_params)
    
    if correlations:
        st.subheader("📈 Notable Correlations")
        
        # Sort by absolute correlation value
        sorted_correlations = sorted(
            correlations.items(), 
            key=lambda x: abs(x[1]['correlation']), 
            reverse=True
        )
        
        for param_pair, corr_data in sorted_correlations[:5]:  # Top 5 correlations
            param1, param2 = param_pair.replace('_vs_', ' vs ').replace('_', ' ').title().split(' Vs ')
            corr_value = corr_data['correlation']
            strength = corr_data['strength'].replace('_', ' ').title()
            
            correlation_emoji = "🔴" if abs(corr_value) > 0.7 else "🟡" if abs(corr_value) > 0.4 else "🟢"
            direction = "positive" if corr_value > 0 else "negative"
            
            st.write(f"{correlation_emoji} **{param1} vs {param2}**: "
                    f"{corr_value:.3f} ({strength} {direction} correlation)")

def display_data_export():
    """Display data export options."""
    st.header("💾 Data Export")
    
    # Date range selection for export
    col1, col2 = st.columns(2)
    with col1:
        export_start_date = st.date_input(
            "Export Start Date",
            value=datetime.now().date() - timedelta(days=30),
            key="export_start"
        )
    with col2:
        export_end_date = st.date_input(
            "Export End Date",
            value=datetime.now().date(),
            key="export_end"
        )
    
    # Export format selection
    export_format = st.selectbox("Export Format", ["CSV", "Excel"], key="export_format")
    
    if st.button("Export Data"):
        db = WeatherDatabase()
        start_datetime = datetime.combine(export_start_date, datetime.min.time())
        end_datetime = datetime.combine(export_end_date, datetime.max.time())
        
        df = db.get_data_by_date_range(start_datetime, end_datetime)
        
        if df.empty:
            st.warning("No data available for the selected date range.")
            return
        
        # Prepare download
        if export_format == "CSV":
            csv_data = df.to_csv(index=False)
            filename = f"weather_data_{export_start_date}_to_{export_end_date}.csv"
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name=filename,
                mime="text/csv"
            )
        else:  # Excel
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Weather Data', index=False)
                
                # Add summary sheet
                summary_stats = df.describe()
                summary_stats.to_excel(writer, sheet_name='Summary Statistics')
            
            filename = f"weather_data_{export_start_date}_to_{export_end_date}.xlsx"
            st.download_button(
                label="📥 Download Excel",
                data=output.getvalue(),
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        st.success(f"✅ Data export ready! ({len(df)} records)")

def main():
    """Main application function."""
    st.title("🌤️ Weather Monitoring & Analysis Platform")
    st.markdown("**GARNI 925T Smart Weather Station Integration**")
    
    # Sidebar configuration
    with st.sidebar:
        st.title("🔧 Control Panel")
        
        # Configuration status
        config_ok = display_configuration_status()
        
        if config_ok:
            # Data collection controls
            collection_status = display_data_collection_controls()
        else:
            st.error("⚠️ Configuration incomplete. Check environment variables.")
            collection_status = {"is_running": False, "database_stats": {}}
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", "📈 Time Series", "📊 Trends", 
        "🔗 Correlations", "🌤️ Current", "💾 Export"
    ])
    
    with tab1:
        display_dashboard_overview()
    
    with tab2:
        display_time_series_analysis()
    
    with tab3:
        display_trend_analysis()
    
    with tab4:
        display_correlation_analysis()
    
    with tab5:
        display_current_conditions()
    
    with tab6:
        display_data_export()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**Weather Monitoring Platform** - Automated data collection from GARNI 925T via Tuya API | "
        "Historical analysis with Meteostat | Built with Streamlit"
    )

if __name__ == "__main__":
    main()
