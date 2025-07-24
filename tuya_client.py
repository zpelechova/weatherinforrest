"""Tuya API client for GARNI 925T weather station integration."""

import requests
import json
import hashlib
import hmac
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from config import (
    TUYA_ACCESS_ID, TUYA_ACCESS_KEY, TUYA_API_ENDPOINT, 
    TUYA_DEVICE_ID, MAX_RETRIES, REQUEST_TIMEOUT
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TuyaWeatherClient:
    """Client for interacting with Tuya API to get weather station data."""
    
    def __init__(self):
        """Initialize Tuya API client."""
        self.access_id = TUYA_ACCESS_ID
        self.access_key = TUYA_ACCESS_KEY
        self.api_endpoint = TUYA_API_ENDPOINT
        self.device_id = TUYA_DEVICE_ID
        self.token = None
        self.token_expires = None
        
        if not all([self.access_id, self.access_key, self.api_endpoint]):
            logger.warning("Tuya API credentials not fully configured")
    
    def _generate_signature(self, method: str, url: str, headers: Dict, 
                          body: str = "") -> str:
        """Generate signature for Tuya API authentication."""
        try:
            # Create string to sign
            string_to_sign = f"{method}\n{hashlib.sha256(body.encode()).hexdigest()}\n"
            string_to_sign += "\n".join([f"{k}:{v}" for k, v in sorted(headers.items())])
            string_to_sign += f"\n{url}"
            
            # Generate signature
            signature = hmac.new(
                self.access_key.encode(),
                string_to_sign.encode(),
                hashlib.sha256
            ).hexdigest().upper()
            
            return signature
        except Exception as e:
            logger.error(f"Error generating signature: {e}")
            return ""
    
    def _get_token(self) -> bool:
        """Get access token from Tuya API."""
        try:
            if (self.token and self.token_expires and 
                datetime.now() < self.token_expires):
                return True
            
            url = f"{self.api_endpoint}/v1.0/token?grant_type=1"
            timestamp = str(int(time.time() * 1000))
            
            headers = {
                "client_id": self.access_id,
                "sign_method": "HMAC-SHA256",
                "t": timestamp,
            }
            
            # Generate signature
            sign = self._generate_signature("GET", url, headers)
            headers["sign"] = sign
            
            response = requests.get(url, headers=headers, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            if data.get("success"):
                result = data.get("result", {})
                self.token = result.get("access_token")
                expire_time = result.get("expire_time", 7200)
                self.token_expires = datetime.now() + timedelta(seconds=expire_time - 60)
                logger.info("Successfully obtained Tuya access token")
                return True
            else:
                logger.error(f"Failed to get token: {data}")
                return False
                
        except Exception as e:
            logger.error(f"Error getting Tuya token: {e}")
            return False
    
    def _make_request(self, method: str, endpoint: str, params: Dict = None,
                     body: Dict = None) -> Optional[Dict]:
        """Make authenticated request to Tuya API."""
        try:
            if not self._get_token():
                return None
            
            url = f"{self.api_endpoint}{endpoint}"
            timestamp = str(int(time.time() * 1000))
            
            headers = {
                "client_id": self.access_id,
                "access_token": self.token,
                "sign_method": "HMAC-SHA256",
                "t": timestamp,
                "Content-Type": "application/json"
            }
            
            # Prepare body
            body_str = json.dumps(body) if body else ""
            
            # Generate signature
            sign = self._generate_signature(method, url, headers, body_str)
            headers["sign"] = sign
            
            # Make request
            for attempt in range(MAX_RETRIES):
                try:
                    if method == "GET":
                        response = requests.get(
                            url, headers=headers, params=params, 
                            timeout=REQUEST_TIMEOUT
                        )
                    elif method == "POST":
                        response = requests.post(
                            url, headers=headers, data=body_str, 
                            timeout=REQUEST_TIMEOUT
                        )
                    else:
                        logger.error(f"Unsupported HTTP method: {method}")
                        return None
                    
                    response.raise_for_status()
                    return response.json()
                    
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request attempt {attempt + 1} failed: {e}")
                    if attempt == MAX_RETRIES - 1:
                        raise
                    time.sleep(2 ** attempt)  # Exponential backoff
            
        except Exception as e:
            logger.error(f"Error making Tuya API request: {e}")
            return None
    
    def get_device_status(self) -> Optional[Dict]:
        """Get current status of the weather station device."""
        if not self.device_id:
            logger.error("Device ID not configured")
            return None
        
        endpoint = f"/v1.0/devices/{self.device_id}/status"
        response = self._make_request("GET", endpoint)
        
        if response and response.get("success"):
            return response.get("result")
        return None
    
    def get_weather_current(self, lat: float, lon: float) -> Optional[Dict]:
        """Get current weather data for specified coordinates."""
        endpoint = "/v1.0/iot-03/weather/current"
        params = {"lat": lat, "lon": lon}
        
        response = self._make_request("GET", endpoint, params=params)
        
        if response and response.get("success"):
            return response.get("result")
        return None
    
    def get_weather_history_24h(self, lat: float, lon: float) -> Optional[List[Dict]]:
        """Get 24-hour weather history for specified coordinates."""
        endpoint = "/v1.0/iot-03/weather/history24h"
        params = {"lat": lat, "lon": lon}
        
        response = self._make_request("GET", endpoint, params=params)
        
        if response and response.get("success"):
            return response.get("result")
        return None
    
    def parse_weather_data(self, raw_data: Dict, source: str = "tuya") -> Dict:
        """Parse raw weather data into standardized format."""
        try:
            if not raw_data:
                return {}
            
            # Handle different data structures from Tuya API
            weather_data = {}
            
            # Extract current weather if available
            current = raw_data.get("current_weather", {})
            if current:
                weather_data.update({
                    "temperature": self._safe_float(current.get("temp")),
                    "humidity": self._safe_float(current.get("humidity")),
                    "pressure": self._safe_float(current.get("pressure")),
                    "wind_speed": self._safe_float(current.get("wind_speed")),
                    "wind_direction": self._safe_float(current.get("wind_dir")),
                    "uv_index": self._safe_float(current.get("uvi")),
                    "feels_like": self._safe_float(current.get("real_feel")),
                    "condition": current.get("condition")
                })
            
            # Extract air quality if available
            air_quality = raw_data.get("air_quality", {})
            if air_quality:
                weather_data.update({
                    "air_quality_aqi": self._safe_int(air_quality.get("aqi")),
                    "air_quality_pm25": self._safe_float(air_quality.get("pm25")),
                    "air_quality_pm10": self._safe_float(air_quality.get("pm10"))
                })
            
            # Handle device status data (for direct device readings)
            if isinstance(raw_data, list):
                for item in raw_data:
                    code = item.get("code", "")
                    value = item.get("value")
                    
                    # Map device codes to standard fields
                    if code == "va_temperature":
                        weather_data["temperature"] = self._safe_float(value)
                    elif code == "va_humidity":
                        weather_data["humidity"] = self._safe_float(value)
                    elif code == "pressure":
                        weather_data["pressure"] = self._safe_float(value)
                    elif code == "wind_speed":
                        weather_data["wind_speed"] = self._safe_float(value)
                    elif code == "wind_direction":
                        weather_data["wind_direction"] = self._safe_float(value)
                    elif code == "rainfall":
                        weather_data["rainfall"] = self._safe_float(value)
                    elif code == "uv":
                        weather_data["uv_index"] = self._safe_float(value)
                    elif code == "solar_radiation":
                        weather_data["solar_radiation"] = self._safe_float(value)
            
            weather_data.update({
                "timestamp": datetime.now().isoformat(),
                "source": source
            })
            
            return weather_data
            
        except Exception as e:
            logger.error(f"Error parsing weather data: {e}")
            return {}
    
    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        try:
            return float(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def _safe_int(self, value) -> Optional[int]:
        """Safely convert value to integer."""
        try:
            return int(value) if value is not None else None
        except (ValueError, TypeError):
            return None
    
    def test_connection(self) -> bool:
        """Test if the Tuya API connection is working."""
        try:
            if not self.access_id or not self.access_key:
                logger.error("Tuya API credentials not configured")
                return False
            
            success = self._get_token()
            if success:
                logger.info("Tuya API connection test successful")
            else:
                logger.error("Tuya API connection test failed")
            
            return success
            
        except Exception as e:
            logger.error(f"Error testing Tuya connection: {e}")
            return False
