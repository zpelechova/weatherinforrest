# How to Link Your GARNI 925T to Tuya Development Platform

## The Problem
Your weather station works in the Smart Life app, but it's not visible in your Tuya developer project. This is why the API calls are failing.

## Solution: Link Your App Account

### Step 1: Access Your Tuya Project
1. Go to https://iot.tuya.com/
2. Navigate to Cloud → Projects → [Your Project]

### Step 2: Link Your Smart Life App Account
1. In your project, click the **"Devices"** tab
2. Click **"Link Tuya App Account"** button
3. You'll see a QR code and instructions

### Step 3: Connect Using Smart Life App
1. Open your **Smart Life app** (where your GARNI 925T works)
2. Go to "Me" → "Settings" → "Account and Security" 
3. Look for "Developer Options" or "Link Account"
4. Scan the QR code from your Tuya developer console

### Step 4: Authorize the Connection
1. Follow the prompts in the Smart Life app
2. Grant permission to link your devices
3. Return to the Tuya developer console

### Step 5: Verify Device Appears
1. Refresh the Devices tab in your Tuya project
2. Your GARNI 925T should now appear in the device list
3. Copy the **Device ID** (22 characters)

## Alternative: Check Cloud Project Region
Make sure your Tuya project region matches where you registered your Smart Life account:
- If you're in Europe: Use **EU Data Center**
- If in Americas: Use **US Data Center**  
- If in Asia: Use **CN Data Center**

## What to Look For
After linking, you should see:
- Device Name: GARNI 925T or similar
- Device ID: 22-character string
- Status: Online/Offline
- Device Type: Weather Station or similar

## Next Steps
Once your device appears in the developer console, I can test the connection again with the proper device ID.