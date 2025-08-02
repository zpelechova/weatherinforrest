"""Timezone utilities for Prague/Central European Time"""

import pytz
from datetime import datetime, timedelta
from config import TIMEZONE

def get_prague_timezone():
    """Get Prague timezone object"""
    return pytz.timezone(TIMEZONE)

def now_prague():
    """Get current time in Prague timezone"""
    prague_tz = get_prague_timezone()
    return datetime.now(prague_tz)

def to_prague_time(dt):
    """Convert datetime to Prague timezone"""
    if dt is None:
        return None
    
    prague_tz = get_prague_timezone()
    
    # If datetime is naive, assume UTC
    if dt.tzinfo is None:
        utc_dt = pytz.UTC.localize(dt)
    else:
        utc_dt = dt
    
    return utc_dt.astimezone(prague_tz)

def format_prague_time(dt, format_str="%Y-%m-%d %H:%M:%S"):
    """Format datetime in Prague timezone"""
    if dt is None:
        return "N/A"
    
    prague_dt = to_prague_time(dt)
    return prague_dt.strftime(format_str)

def prague_time_info():
    """Get Prague timezone information"""
    prague_tz = get_prague_timezone()
    now = now_prague()
    
    return {
        'timezone': TIMEZONE,
        'current_time': now,
        'offset': now.strftime('%z'),
        'is_dst': now.dst() != timedelta(0) if hasattr(now, 'dst') else False
    }