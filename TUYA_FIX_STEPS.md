# Fix GARNI 925T Connection - Step by Step

## Current Issue Analysis
✅ Credentials format is correct (ACCESS_ID: a35gfn8k..., DEVICE_ID: bf5f5736feb7d67046gdkw)
✅ All Tuya endpoints are reachable
✅ Signature generation is working correctly
❌ All endpoints return "sign invalid" error

This pattern indicates: **Project configuration or device linking issue**

## Solution Steps (Try in Order)

### Step 1: Verify Project Region
**Current Device ID**: bf5f5736feb7d67046gdkw

1. In Tuya IoT Platform (https://iot.tuya.com/)
2. Click your profile (top right)
3. Check "Data Center" setting
4. **Important**: This must match where your Smart Life account was registered
   - Europe/EMEA → EU Data Center
   - Americas → Western America Data Center  
   - Asia-Pacific → China Data Center

**If wrong region**: Create new project in correct data center

### Step 2: Enable ALL Required APIs
In your project → API tab, ensure these are enabled:

**Required for Weather Stations:**
- ✅ IoT Core
- ✅ Authorization Management  
- ✅ Device Status Notification
- ✅ Device Control
- ✅ Smart Home Device Management

**Additional APIs to Enable:**
- ✅ IoT Data Analytics
- ✅ Device Management
- ✅ Industry Capabilities

### Step 3: Re-link Your Device Account
1. Go to Devices tab → "Link Tuya App Account"
2. **Important**: Log out of Smart Life app first
3. Log back into Smart Life app
4. In Smart Life: Profile → Privacy Settings → Data Management
5. Look for "Third-party Services" or "Developer Authorization"
6. Authorize your developer project

### Step 4: Verify Device Appears
After linking, your GARNI 925T should appear in Devices tab with:
- Name: Weather Station or GARNI 925T
- Status: Online
- Device ID: bf5f5736feb7d67046gdkw

### Step 5: Generate Fresh Credentials
1. In project Overview tab
2. Click "Reset" next to Access Secret
3. Copy NEW Access ID and Access Secret
4. Update in system

## Test After Each Step
After each step, I'll test the connection for you.

## Which Step Should We Try First?
Based on the error pattern, I recommend starting with **Step 1: Project Region** - this is the most common cause of persistent "sign invalid" errors.