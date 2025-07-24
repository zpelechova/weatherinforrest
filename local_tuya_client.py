"""Local Tuya client for direct GARNI 925T weather station access."""

import tinytuya
import json
import time
import logging
from typing import Dict, Optional
from config import TUYA_DEVICE_ID

logger = logging.getLogger(__name__)

class LocalTuyaWeatherClient:
    """Client for local Tuya device communication."""
    
    def __init__(self):
        """Initialize local Tuya client."""
        self.device_id = TUYA_DEVICE_ID
        self.device = None
        self.device_ip = None
        self.local_key = None
        
    def discover_devices(self) -> Dict:
        """Discover Tuya devices on local network."""
        try:
            logger.info("Scanning for Tuya devices on local network...")
            devices = tinytuya.deviceScan(verbose=False, maxretry=3)
            
            logger.info(f"Found {len(devices)} Tuya devices on network")
            
            # Look for our specific device
            for device in devices:
                if device.get('gwId') == self.device_id:
                    logger.info(f"Found GARNI 925T weather station at {device.get('ip')}")
                    return device
                    
            # If not found by ID, list all devices for debugging
            if devices:
                logger.info("Available devices:")
                for i, device in enumerate(devices):
                    logger.info(f"  {i+1}. ID: {device.get('gwId', 'Unknown')} "
                              f"IP: {device.get('ip', 'Unknown')} "
                              f"Version: {device.get('version', 'Unknown')}")
            
            return {}
            
        except Exception as e:
            logger.error(f"Device discovery failed: {e}")
            return {}
    
    def connect_to_device(self, device_ip: str = None, local_key: str = None) -> bool:
        """Connect to the weather station locally."""
        try:
            if not device_ip:
                # Try to discover device
                discovered = self.discover_devices()
                if discovered:
                    device_ip = discovered.get('ip')
                    
            if not device_ip:
                logger.warning("No device IP found. Device may not be on local network.")
                return False
                
            # Try different connection methods
            versions = [3.1, 3.3, 3.4]
            
            for version in versions:
                try:
                    logger.info(f"Attempting connection to {device_ip} with version {version}")
                    
                    # Connect without local key first (some devices allow status reading)
                    self.device = tinytuya.Device(
                        dev_id=self.device_id,
                        address=device_ip,
                        local_key='',  # Try without key first
                        version=version
                    )
                    
                    # Test connection
                    status = self.device.status()
                    
                    if 'Error' not in str(status):
                        logger.info(f"Successfully connected with version {version}")
                        self.device_ip = device_ip
                        return True
                        
                except Exception as e:
                    logger.debug(f"Version {version} failed: {e}")
                    continue
            
            logger.warning("Could not establish local connection to weather station")
            return False
            
        except Exception as e:
            logger.error(f"Local connection failed: {e}")
            return False
    
    def get_weather_data(self) -> Optional[Dict]:
        """Get weather data from local device."""
        try:
            if not self.device:
                logger.warning("Device not connected. Attempting to connect...")
                if not self.connect_to_device():
                    return None
            
            # Get device status
            status = self.device.status()
            
            if 'Error' in str(status):
                logger.error(f"Device returned error: {status}")
                return None
            
            # Parse weather data from device status
            weather_data = self._parse_weather_data(status)
            
            if weather_data:
                logger.info("Successfully retrieved weather data from local device")
                return weather_data
            else:
                logger.warning("No weather data found in device response")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get weather data: {e}")
            return None
    
    def _parse_weather_data(self, device_status: Dict) -> Optional[Dict]:
        """Parse weather data from device status response."""
        try:
            # Extract data points (DPs) from device response
            dps = device_status.get('dps', {})
            
            if not dps:
                logger.warning("No data points found in device response")
                return None
            
            # Common GARNI 925T data point mappings
            # These may vary by device, so we'll try to detect automatically
            weather_data = {
                'timestamp': time.time(),
                'source': 'local_tuya'
            }
            
            # Try to map common data points
            dp_mappings = {
                '1': 'temperature',      # Usually temperature in °C * 10
                '2': 'humidity',         # Humidity percentage
                '3': 'wind_speed',       # Wind speed
                '4': 'wind_direction',   # Wind direction in degrees
                '5': 'uv_index',         # UV index
                '6': 'solar_radiation',  # Light/solar radiation
                '7': 'rainfall',         # Rainfall
                '8': 'pressure',         # Atmospheric pressure
            }
            
            for dp_id, value in dps.items():
                dp_name = dp_mappings.get(str(dp_id))
                if dp_name and value is not None:
                    # Convert temperature if needed (often comes as integer * 10)
                    if dp_name == 'temperature' and isinstance(value, int) and value > 100:
                        value = value / 10.0
                    elif dp_name == 'humidity' and isinstance(value, int) and value > 100:
                        value = value / 10.0
                    
                    weather_data[dp_name] = value
            
            # Log discovered data points for debugging
            logger.info(f"Raw device data points: {dps}")
            logger.info(f"Parsed weather data: {weather_data}")
            
            return weather_data if len(weather_data) > 2 else None  # Must have more than timestamp + source
            
        except Exception as e:
            logger.error(f"Failed to parse weather data: {e}")
            return None
    
    def test_connection(self) -> bool:
        """Test local connection to weather station."""
        try:
            logger.info("Testing local Tuya connection...")
            
            # First try device discovery
            discovered = self.discover_devices()
            
            if discovered:
                logger.info("✓ Device discovered on local network")
                
                # Try to connect and get data
                if self.connect_to_device():
                    data = self.get_weather_data()
                    if data:
                        logger.info("✓ Successfully retrieved weather data")
                        return True
                    else:
                        logger.warning("⚠ Connected but no weather data available")
                        return False
                else:
                    logger.warning("⚠ Device found but connection failed")
                    return False
            else:
                logger.warning("⚠ No compatible devices found on local network")
                return False
                
        except Exception as e:
            logger.error(f"Local connection test failed: {e}")
            return False

# Factory function for compatibility
def get_local_tuya_client() -> LocalTuyaWeatherClient:
    """Get local Tuya weather client instance."""
    return LocalTuyaWeatherClient()