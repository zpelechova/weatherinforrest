# How to Get Correct Tuya API Tokens

## Step 1: Access Tuya IoT Platform
1. Go to https://iot.tuya.com/
2. Log in with your Tuya account (same account used for Smart Life app)

## Step 2: Navigate to Your Project
1. Click "Cloud" in the top menu
2. Click "Projects" 
3. Find your project (or create a new one if needed)
4. Click on your project name to enter it

## Step 3: Get API Credentials
1. In your project, click the "Overview" tab
2. You'll see two important values:
   - **Access ID** (also called Client ID) - 20 characters
   - **Access Secret** (also called Client Secret) - 32 characters
3. Copy these EXACT values (watch for spaces or extra characters)

## Step 4: Enable Required APIs
1. Still in your project, click "API" tab
2. Make sure these services are enabled:
   - IoT Core ✓
   - Smart Home Device Management ✓ 
   - Device Status Notification ✓
   - Device Control ✓

## Step 5: Get Device ID
1. Click "Devices" tab in your project
2. Click "Link Tuya App Account" 
3. Follow the steps to link your Smart Life app account
4. Your GARNI 925T should appear in the device list
5. Copy the Device ID (22 characters long)

## Step 6: Check Region
Make sure your project region matches where your device is located:
- Europe: EU
- Americas: US
- Asia: CN

## What You Need to Provide
After following these steps, you'll have:
- TUYA_ACCESS_ID (20 characters)
- TUYA_ACCESS_KEY (32 characters) 
- TUYA_DEVICE_ID (22 characters)

These will replace your current tokens in the system.