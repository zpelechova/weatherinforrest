"""Weather data analysis and visualization functions."""

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class WeatherAnalyzer:
    """Weather data analysis and trend identification."""
    
    def __init__(self, df: pd.DataFrame):
        """Initialize with weather data DataFrame."""
        self.df = df.copy()
        if not self.df.empty:
            self.df['timestamp'] = pd.to_datetime(self.df['timestamp'])
            self.df = self.df.sort_values('timestamp')
    
    def calculate_trends(self, parameter: str, window_days: int = 7) -> Dict:
        """Calculate trend statistics for a weather parameter."""
        try:
            if self.df.empty or parameter not in self.df.columns:
                return {}
            
            # Filter out null values
            data = self.df[self.df[parameter].notna()][['timestamp', parameter]]
            if data.empty:
                return {}
            
            # Calculate rolling averages
            data = data.set_index('timestamp')
            rolling_mean = data[parameter].rolling(window=f'{window_days}D').mean()
            
            # Calculate trend direction
            recent_mean = rolling_mean.tail(window_days).mean()
            previous_mean = rolling_mean.tail(window_days * 2).head(window_days).mean()
            
            if pd.isna(recent_mean) or pd.isna(previous_mean):
                trend_direction = "insufficient_data"
                trend_change = 0
            else:
                trend_change = recent_mean - previous_mean
                if abs(trend_change) < data[parameter].std() * 0.1:
                    trend_direction = "stable"
                elif trend_change > 0:
                    trend_direction = "increasing"
                else:
                    trend_direction = "decreasing"
            
            return {
                "current_value": data[parameter].iloc[-1] if not data.empty else None,
                "mean": data[parameter].mean(),
                "min": data[parameter].min(),
                "max": data[parameter].max(),
                "std": data[parameter].std(),
                "trend_direction": trend_direction,
                "trend_change": trend_change,
                "data_points": len(data)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trends for {parameter}: {e}")
            return {}
    
    def detect_anomalies(self, parameter: str, threshold_std: float = 2.0) -> List[Dict]:
        """Detect anomalies in weather data using statistical methods."""
        try:
            if self.df.empty or parameter not in self.df.columns:
                return []
            
            data = self.df[self.df[parameter].notna()][['timestamp', parameter]]
            if len(data) < 10:  # Need sufficient data for anomaly detection
                return []
            
            # Calculate z-scores
            mean_val = data[parameter].mean()
            std_val = data[parameter].std()
            
            if std_val == 0:  # No variation in data
                return []
            
            data['z_score'] = (data[parameter] - mean_val) / std_val
            
            # Find anomalies
            anomalies = data[abs(data['z_score']) > threshold_std]
            
            anomaly_list = []
            for _, row in anomalies.iterrows():
                anomaly_list.append({
                    "timestamp": row['timestamp'].isoformat(),
                    "value": row[parameter],
                    "z_score": row['z_score'],
                    "severity": "high" if abs(row['z_score']) > 3.0 else "moderate"
                })
            
            return anomaly_list
            
        except Exception as e:
            logger.error(f"Error detecting anomalies for {parameter}: {e}")
            return []
    
    def get_daily_patterns(self, parameter: str) -> Dict:
        """Analyze daily patterns in weather data."""
        try:
            if self.df.empty or parameter not in self.df.columns:
                return {}
            
            data = self.df[self.df[parameter].notna()][['timestamp', parameter]]
            if data.empty:
                return {}
            
            # Extract hour from timestamp
            data['hour'] = data['timestamp'].dt.hour
            
            # Calculate hourly averages
            hourly_avg = data.groupby('hour')[parameter].agg(['mean', 'std']).reset_index()
            
            return {
                "hourly_averages": hourly_avg.to_dict('records'),
                "peak_hour": hourly_avg.loc[hourly_avg['mean'].idxmax(), 'hour'],
                "low_hour": hourly_avg.loc[hourly_avg['mean'].idxmin(), 'hour'],
                "daily_range": hourly_avg['mean'].max() - hourly_avg['mean'].min()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing daily patterns for {parameter}: {e}")
            return {}
    
    def calculate_correlations(self, parameters: List[str]) -> Dict:
        """Calculate correlations between weather parameters."""
        try:
            if self.df.empty:
                return {}
            
            # Filter for available parameters
            available_params = [p for p in parameters if p in self.df.columns]
            if len(available_params) < 2:
                return {}
            
            correlation_matrix = self.df[available_params].corr()
            
            # Convert to dictionary format
            correlations = {}
            for i, param1 in enumerate(available_params):
                for j, param2 in enumerate(available_params):
                    if i < j:  # Avoid duplicates
                        corr_value = correlation_matrix.loc[param1, param2]
                        if not pd.isna(corr_value):
                            correlations[f"{param1}_vs_{param2}"] = {
                                "correlation": corr_value,
                                "strength": self._interpret_correlation(abs(corr_value))
                            }
            
            return correlations
            
        except Exception as e:
            logger.error(f"Error calculating correlations: {e}")
            return {}
    
    def _interpret_correlation(self, corr_value: float) -> str:
        """Interpret correlation strength."""
        if corr_value >= 0.8:
            return "very_strong"
        elif corr_value >= 0.6:
            return "strong"
        elif corr_value >= 0.4:
            return "moderate"
        elif corr_value >= 0.2:
            return "weak"
        else:
            return "very_weak"

def create_time_series_chart(df: pd.DataFrame, parameter: str, title: str) -> go.Figure:
    """Create an interactive time series chart."""
    try:
        if df.empty or parameter not in df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Filter non-null values
        data = df[df[parameter].notna()]
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for this parameter",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        fig = go.Figure()
        
        # Add main trace
        fig.add_trace(go.Scatter(
            x=data['timestamp'],
            y=data[parameter],
            mode='lines+markers',
            name=parameter.replace('_', ' ').title(),
            line=dict(width=2),
            marker=dict(size=4),
            hovertemplate=f"<b>%{{x}}</b><br>{parameter}: %{{y}}<extra></extra>"
        ))
        
        # Add rolling average if enough data
        if len(data) > 24:
            data_indexed = data.set_index('timestamp')
            rolling_avg = data_indexed[parameter].rolling(window=24, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=rolling_avg.index,
                y=rolling_avg.values,
                mode='lines',
                name='24h Average',
                line=dict(width=3, dash='dash'),
                hovertemplate=f"<b>%{{x}}</b><br>24h Avg: %{{y:.2f}}<extra></extra>"
            ))
        
        fig.update_layout(
            title=title,
            xaxis_title="Time",
            yaxis_title=parameter.replace('_', ' ').title(),
            hovermode='x unified',
            showlegend=True,
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating time series chart for {parameter}: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

def create_correlation_heatmap(df: pd.DataFrame, parameters: List[str]) -> go.Figure:
    """Create a correlation heatmap."""
    try:
        # Filter for available parameters
        available_params = [p for p in parameters if p in df.columns]
        
        if len(available_params) < 2:
            fig = go.Figure()
            fig.add_annotation(
                text="Not enough parameters for correlation analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        correlation_matrix = df[available_params].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.values.round(2),
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate="<b>%{x} vs %{y}</b><br>Correlation: %{z:.3f}<extra></extra>"
        ))
        
        fig.update_layout(
            title="Weather Parameters Correlation Matrix",
            height=400,
            width=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating correlation heatmap: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating heatmap: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

def create_daily_pattern_chart(df: pd.DataFrame, parameter: str) -> go.Figure:
    """Create a daily pattern analysis chart."""
    try:
        if df.empty or parameter not in df.columns:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        data = df[df[parameter].notna()].copy()
        if data.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for this parameter",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Convert timestamp to datetime for grouping
        data['timestamp'] = pd.to_datetime(data['timestamp'])
        data['hour'] = data['timestamp'].dt.hour
        hourly_stats = data.groupby('hour')[parameter].agg(['mean', 'std']).reset_index()
        
        fig = go.Figure()
        
        # Add mean line
        fig.add_trace(go.Scatter(
            x=hourly_stats['hour'],
            y=hourly_stats['mean'],
            mode='lines+markers',
            name='Average',
            line=dict(width=3),
            marker=dict(size=6)
        ))
        
        # Add confidence interval
        fig.add_trace(go.Scatter(
            x=list(hourly_stats['hour']) + list(hourly_stats['hour'][::-1]),
            y=list(hourly_stats['mean'] + hourly_stats['std']) + 
              list((hourly_stats['mean'] - hourly_stats['std'])[::-1]),
            fill='tonexty',
            fillcolor='rgba(0,100,80,0.2)',
            line=dict(color='rgba(255,255,255,0)'),
            name='±1 Std Dev',
            showlegend=True
        ))
        
        fig.update_layout(
            title=f"Daily Pattern - {parameter.replace('_', ' ').title()}",
            xaxis_title="Hour of Day",
            yaxis_title=parameter.replace('_', ' ').title(),
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating daily pattern chart for {parameter}: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating chart: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig

def create_summary_dashboard(df: pd.DataFrame) -> go.Figure:
    """Create a comprehensive dashboard with multiple weather parameters."""
    try:
        if df.empty:
            fig = go.Figure()
            fig.add_annotation(
                text="No data available for dashboard",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Define parameters to display
        params = ['temperature', 'humidity', 'pressure', 'wind_speed']
        available_params = [p for p in params if p in df.columns and df[p].notna().any()]
        
        if not available_params:
            fig = go.Figure()
            fig.add_annotation(
                text="No weather parameters available",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False
            )
            return fig
        
        # Create subplots
        rows = 2
        cols = 2
        fig = make_subplots(
            rows=rows, cols=cols,
            subplot_titles=[p.replace('_', ' ').title() for p in available_params[:4]],
            vertical_spacing=0.1,
            horizontal_spacing=0.1
        )
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
        
        for i, param in enumerate(available_params[:4]):
            row = (i // cols) + 1
            col = (i % cols) + 1
            
            data = df[df[param].notna()]
            
            fig.add_trace(
                go.Scatter(
                    x=data['timestamp'],
                    y=data[param],
                    mode='lines',
                    name=param.replace('_', ' ').title(),
                    line=dict(color=colors[i], width=2),
                    showlegend=False
                ),
                row=row, col=col
            )
        
        fig.update_layout(
            title="Weather Station Dashboard",
            height=600,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating summary dashboard: {e}")
        fig = go.Figure()
        fig.add_annotation(
            text=f"Error creating dashboard: {str(e)}",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False
        )
        return fig
