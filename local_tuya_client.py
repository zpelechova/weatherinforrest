"""Local Tuya client for GARNI 925T weather station - bypasses cloud API issues."""

import json
import socket
import time
import struct
import hashlib
import hmac
import os
from datetime import datetime

# Device information
TUYA_DEVICE_ID = os.getenv('NEW_TUYA_DEVICE_ID', 'bf5f5736feb7d67046gdkw')

class LocalTuyaClient:
    """Local connection to GARNI 925T weather station."""
    
    def __init__(self):
        self.device_id = TUYA_DEVICE_ID
        self.local_key = None  # Will need to be obtained separately
        self.ip_address = None
        self.version = 3.3
        
    def scan_for_device(self):
        """Scan local network for GARNI 925T weather station."""
        print("Scanning local network for GARNI 925T weather station...")
        
        # Try to find device on local network
        found_devices = []
        
        # Common weather station ports
        ports = [6668, 6669, 6670]
        
        # Scan local network (simple approach)
        import subprocess
        
        try:
            # Get local IP range
            result = subprocess.run(['ip', 'route'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'src' in line and '192.168' in line:
                        # Extract network range
                        parts = line.split()
                        for part in parts:
                            if '192.168' in part and '/' in part:
                                network = part.split('/')[0]
                                base_ip = '.'.join(network.split('.')[:-1])
                                
                                print(f"Scanning network: {base_ip}.0/24")
                                
                                # Scan common IPs
                                for i in range(1, 255):
                                    ip = f"{base_ip}.{i}"
                                    for port in ports:
                                        if self.test_connection(ip, port):
                                            found_devices.append((ip, port))
                                            print(f"Found potential device at {ip}:{port}")
                                
                                break
                        break
        except Exception as e:
            print(f"Network scan failed: {e}")
        
        return found_devices
    
    def test_connection(self, ip, port, timeout=1):
        """Test if device responds on given IP and port."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return result == 0
        except:
            return False
    
    def get_weather_data_simulation(self):
        """Simulate weather data until real connection is established."""
        print("GARNI 925T Cloud API unavailable - providing simulation mode...")
        print("To get real data, we need:")
        print("1. Local network access to your weather station")
        print("2. Device local key (extracted from Smart Life app)")
        print("3. Direct IP connection to bypass cloud API")
        
        # Provide realistic simulation based on Kozlovice weather patterns
        import random
        current_time = datetime.now()
        
        # Kozlovice-like weather simulation
        base_temp = 15 + 10 * random.random()  # 15-25°C range
        humidity = 45 + 30 * random.random()   # 45-75% range
        pressure = 1010 + 20 * random.random() # 1010-1030 hPa
        
        simulated_data = {
            'timestamp': current_time.isoformat(),
            'temperature': round(base_temp, 1),
            'humidity': round(humidity, 1),
            'pressure': round(pressure, 1),
            'source': 'simulation',
            'device_id': self.device_id,
            'location': 'Kozlovice (50.4489643, 14.3095035)',
            'note': 'Simulated data - GARNI 925T cloud connection unavailable'
        }
        
        return simulated_data
    
    def try_alternative_connection(self):
        """Try alternative connection methods."""
        print("\n=== Alternative Connection Attempts ===")
        
        print("1. Testing local network scan...")
        devices = self.scan_for_device()
        if devices:
            print(f"Found potential devices: {devices}")
            return True
        else:
            print("No local devices found")
        
        print("\n2. Checking if device is on WiFi network...")
        # Could implement mDNS discovery here
        print("mDNS scan not implemented - would need additional libraries")
        
        print("\n3. Manual IP configuration option...")
        print("You could manually provide device IP if known")
        
        return False

def test_local_connection():
    """Test local connection to GARNI 925T."""
    print("=== GARNI 925T Local Connection Test ===\n")
    
    client = LocalTuyaClient()
    
    print(f"Target device: {client.device_id}")
    print("Testing alternative connection methods...\n")
    
    # Try alternative connection
    success = client.try_alternative_connection()
    
    if not success:
        print("\n=== Fallback: Simulation Mode ===")
        weather_data = client.get_weather_data_simulation()
        print("Sample weather data:")
        print(json.dumps(weather_data, indent=2))
        
        print("\n=== Next Steps ===")
        print("For real GARNI 925T data, you have several options:")
        print("1. Contact Tuya support about the API 'sign invalid' issue")
        print("2. Try local network connection with device local key")
        print("3. Use Smart Life app export if available")
        print("4. Monitor using the weather station's own display")
        
        return weather_data
    
    return None

class LocalTuyaWeatherClient:
    """Weather client that works without cloud API for compatibility."""
    
    def __init__(self):
        self.client = LocalTuyaClient()
        self.connection_status = "simulation_mode"
        self.last_error = "Cloud API unavailable - using simulation"
    
    def get_weather_data(self):
        """Get weather data - simulation until API is fixed."""
        return self.client.get_weather_data_simulation()
    
    def test_connection(self):
        """Test connection - always returns False for simulation mode."""
        return False

if __name__ == "__main__":
    test_local_connection()