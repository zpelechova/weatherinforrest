# GARNI 925T Weather Station Setup Guide

This guide will help you connect your GARNI 925T SMART weather station to the monitoring platform.

## Step 1: Create Tuya Developer Account

1. **Go to Tuya IoT Platform**
   - Visit: https://iot.tuya.com
   - Click "Sign Up" if you don't have an account
   - Use the same email you used for the Tuya Smart app

2. **Create a Cloud Development Project**
   - After logging in, click "Cloud Development" 
   - Click "Create Cloud Project"
   - Fill in the project details:
     - Project Name: "Weather Station Monitor" (or any name you prefer)
     - Description: "Weather data collection from GARNI 925T"
     - Industry: "Smart Home" or "Agriculture"
     - Development Method: "Smart Home PaaS"
   - Click "Create"

3. **Get Your API Credentials**
   - Once the project is created, you'll see the project overview
   - Note down these important values:
     - **Access ID / Client ID**: This is your TUYA_ACCESS_ID
     - **Access Secret / Client Secret**: This is your TUYA_ACCESS_KEY
   - Click "Overview" if you need to see them again

## Step 2: Find Your Device ID

### Method 1: Using Tuya Smart App (Easiest)
1. Open the "Tuya Smart" or "Smart Life" app on your phone
2. Find your GARNI 925T weather station in the device list
3. Tap on the device to open its control panel
4. Tap the pencil/edit icon (usually top right)
5. Tap "Device Information" or similar option
6. Look for "Device ID" - this is a long string like "bf1234567890abcdef"
7. Copy this Device ID

### Method 2: Using Tuya Developer Platform
1. In your Tuya IoT project, go to "Devices" tab
2. Click "Link Tuya App Account" 
3. Scan the QR code with your Tuya Smart app
4. Your devices will appear in the list
5. Find your weather station and copy the Device ID

## Step 3: Configure Your Location

You'll also need your weather station's location coordinates:

1. **Find Your Coordinates**:
   - Go to https://www.google.com/maps
   - Find your weather station location
   - Right-click on the exact spot
   - Copy the coordinates (e.g., "50.0755, 14.4378")
   - The first number is LATITUDE, second is LONGITUDE

## Step 4: Enter Credentials in the Platform

Once you have all the information:

1. **TUYA_ACCESS_ID**: Your project's Access ID from step 1
2. **TUYA_ACCESS_KEY**: Your project's Access Secret from step 1  
3. **TUYA_DEVICE_ID**: Your weather station's Device ID from step 2
4. **STATION_LATITUDE**: Your location's latitude (e.g., 50.0755)
5. **STATION_LONGITUDE**: Your location's longitude (e.g., 14.4378)

## Troubleshooting

### Common Issues:

1. **"Device not found" error**:
   - Make sure the Device ID is correct
   - Ensure your weather station is online in the Tuya Smart app

2. **"Authentication failed" error**:
   - Double-check your Access ID and Access Secret
   - Make sure you're using the correct Tuya server region

3. **"No data received" error**:
   - Your weather station might need to be added to your Tuya project
   - Try unlinking and relinking your Tuya app account in the developer platform

### Server Regions:
- **China**: https://openapi.tuyacn.com
- **Americas**: https://openapi.tuyaus.com  
- **Europe**: https://openapi.tuyaeu.com
- **India**: https://openapi.tuyain.com

Choose the server closest to your location for better performance.

## What Happens After Setup

Once configured, the platform will:
- Automatically collect data from your weather station every 15 minutes
- Store all historical data in a local database
- Generate trend analysis and visualizations
- Allow you to export data for further analysis
- Detect unusual weather patterns and anomalies

The system can also supplement your weather station data with additional meteorological data from external sources for comprehensive analysis.