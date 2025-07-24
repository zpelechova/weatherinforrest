# Tuya Weather Station Connection Troubleshooting

## Current Issue
The GARNI 925T weather station is not connecting through the Tuya Cloud API due to "sign invalid" errors.

## Steps to Fix Tuya Connection

### 1. Verify Tuya Developer Account Setup
- Log into https://iot.tuya.com/
- Go to "Cloud" → "Projects"
- Ensure your project has these APIs enabled:
  - IoT Core
  - Device Status Notification
  - Device Control
  - Smart Home Device Management

### 2. Check API Credentials
- In your Tuya project, go to "Overview" tab
- Copy the **exact** values for:
  - Access ID (Client ID)
  - Access Secret (Client Secret)
- Make sure there are no extra spaces or characters

### 3. Device Registration
- Go to "Devices" → "Link Tuya App Account"
- Ensure your GARNI 925T is properly linked to the same account
- Note the Device ID (should be 22 characters long)

### 4. Regional Endpoint
The system tries multiple endpoints:
- EU: https://openapi.tuyaeu.com
- US: https://openapi.tuyaus.com  
- CN: https://openapi.tuyacn.com

Make sure your project region matches your device location.

### 5. Alternative Solutions

#### Option A: Local Integration
Some weather stations support local WiFi connections that bypass cloud APIs.

#### Option B: MQTT Integration
Check if your weather station supports MQTT protocol for direct local access.

#### Option C: Smart Life App Integration
Verify the station works in the Smart Life mobile app first.

## Current Fallback
The system is using Meteostat weather service to provide real weather data for your location while the Tuya connection is being resolved.

## Next Steps
1. Update your Tuya API credentials with the exact values from your developer console
2. Verify device permissions and regional settings
3. Test the connection with fresh credentials