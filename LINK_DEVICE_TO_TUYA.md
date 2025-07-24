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

### Step 3: Connect Using Smart Life App (Multiple Methods)

**Method A: Through Profile Settings**
1. Open Smart Life app → "Profile" (bottom right)
2. Tap the gear icon (Settings) in top right
3. Look for "Account and Security" or "Privacy Settings"
4. Find "Third-party Services" or "Developer Mode"
5. Scan QR code or enter authorization code

**Method B: Through Device Sharing**
1. In Smart Life app, go to your GARNI 925T device
2. Tap the three dots (⋯) or gear icon
3. Look for "Share Device" or "Device Settings"
4. Find "Developer Access" or "API Access"

**Method C: Manual Authorization Code**
1. In Tuya developer console, look for "Authorization Code" instead of QR
2. Copy the code
3. In Smart Life app → Profile → Settings
4. Find "Authorization Code" input field
5. Paste the code from developer console

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