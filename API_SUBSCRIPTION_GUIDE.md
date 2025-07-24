# Tuya API Service Subscription Guide

## Problem Identified
You have a **Trial Edition** subscription but still getting "sign invalid" errors. This is because you need to subscribe to **specific API services** within your project.

## Required API Services for Weather Station

To access your GARNI 925T weather station data, you need these specific API services:

### Essential Services (Must Subscribe)
1. **IoT Core** ✅ (You already have this with Trial)
2. **Smart Home Basic Service** ❌ (Likely missing)
3. **Authorization Management** ❌ (Likely missing) 
4. **Device Status Notification** ❌ (Likely missing)
5. **Industry Basic Service** ❌ (Likely missing)

## Step-by-Step Subscription Process

### 1. Access Your Tuya IoT Project
- Go to: https://iot.tuya.com/
- Login with your account
- Select your project (the one with GARNI 925T device)

### 2. Navigate to Cloud Services
- Click **Cloud** in the left menu
- Select **API Explorer** or **Cloud Services**
- Look for **API Services** or **Service Management**

### 3. Subscribe to Required Services
For each service listed above:
- Search for the service name
- Click **Subscribe** 
- Click **Authorize** for your project
- Confirm the subscription

### 4. Key Services to Find and Subscribe

**Smart Home Basic Service:**
- Provides device control and status APIs
- Essential for getting weather station data

**Authorization Management:**
- Handles API authentication
- Required for token generation

**Device Status Notification:**
- Allows real-time device status updates
- Important for live weather data

**Industry Basic Service:**
- Additional device management APIs
- Supports various device types

### 5. Alternative Method - API Explorer
1. Go to: https://iot.tuya.com/cloud/explorer
2. Try any API call (like "Get Device Details")
3. If it prompts to subscribe to services, follow the prompts
4. Subscribe to all suggested services

## Verification Steps

After subscribing to all services:
1. Wait 5-10 minutes for changes to propagate
2. Run the API test again in your weather app
3. The "sign invalid" error should disappear

## Quick Test Commands

Once subscribed, test with:
```bash
python test_api_now.py
```

The status should change from "API Access Denied" to "Connected"

## Important Notes

- Trial subscriptions are free but have usage limits
- All subscriptions must be authorized for your specific project
- Changes may take 5-10 minutes to take effect
- If services aren't available, contact Tuya support

## Expected Result

After completing these subscriptions:
✅ API authentication will work
✅ Weather station data will be accessible  
✅ Your monitoring system will start collecting data
✅ Dashboard will show live weather information