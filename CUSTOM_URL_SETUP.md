# Setting Up Custom URL: weatherinforrest.replit.app

## How to Get Your Custom Subdomain

### Option 1: New Deployment with Custom Subdomain
1. **Go to Deployments tab** in your Replit interface
2. **Create a new deployment** (Static or Reserved VM)
3. **In the subdomain field**, enter: `weatherinforrest`
4. **Deploy** - your app will be accessible at `weatherinforrest.replit.app`

### Option 2: Modify Existing Deployment
1. **Open Deployments tab**
2. **Go to Settings** of your current deployment
3. **Look for subdomain/hostname settings**
4. **Change subdomain** to `weatherinforrest`
5. **Save and redeploy**

## Deployment Types for Custom Subdomains

### Static Deployment
- Best for: Apps that don't need always-on background processes
- Cost: Free tier available
- URL format: `weatherinforrest.replit.app`

### Reserved VM Deployment  
- Best for: Apps with background processes (like your weather collection)
- Cost: Paid service
- URL format: `weatherinforrest.replit.app`
- Benefits: Guaranteed uptime, background tasks continue

## Important for Your Weather App

Since your weather monitoring system needs:
- Automatic data collection every 5 minutes
- Background processes running continuously
- Database persistence

**Recommended: Reserved VM Deployment** with custom subdomain

## Steps for Weather App Deployment

1. **Configure Reserved VM Deployment**
2. **Set subdomain**: `weatherinforrest`
3. **Ensure environment variables** are configured:
   - TUYA_ACCESS_ID
   - TUYA_ACCESS_KEY  
   - NEW_TUYA_DEVICE_ID
   - STATION_LATITUDE
   - STATION_LONGITUDE

4. **Deploy** - your weather monitoring will be live at `weatherinforrest.replit.app`

## Current Status
Your weather data collection is active locally. After deployment with custom subdomain:
- URL: `https://weatherinforrest.replit.app`
- Automatic collection: Continues every 5 minutes
- Data: All current data transfers to deployed version
- Access: Public weather monitoring dashboard

The custom subdomain makes your weather station easily memorable and shareable.