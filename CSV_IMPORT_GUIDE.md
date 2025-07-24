# How to Import Historical Data from Smart Life App

## Step-by-Step Guide to Export CSV from Smart Life App

### Method 1: Export from Smart Life App

1. **Open Smart Life App** on your phone or tablet

2. **Find Your GARNI 925T Device**
   - Look for your weather station in the device list
   - Tap on the device to open it

3. **Access Historical Data**
   - Look for these sections in your device:
     - "History" 
     - "Statistics"
     - "Data"
     - "Reports"
     - "Charts" 
   - Usually found as tabs or menu options

4. **Find Export Option**
   - Look for buttons labeled:
     - "Export"
     - "Share"
     - "Download"
     - "Save"
     - Three dots menu (⋯) with export option
   - May be in top-right corner or bottom menu

5. **Choose Export Format**
   - Select **CSV** or **Excel** format
   - Choose date range (select maximum available)

6. **Save the File**
   - Save to your device or share via email/cloud

### Method 2: Alternative Access Points

If you can't find export in the main device view, try:

- **Device Settings** → Look for "Data Export" or "History Export"
- **Account Settings** → "Data Management" → "Export Data"
- **Help/Support** section → "Export Data"

## How to Upload CSV to Your Weather Dashboard

1. **Open Your Weather Dashboard** 
   - Navigate to the "Export" section
   - Scroll down to "Import Historical Data from Smart Life App"

2. **Upload Your File**
   - Click "Browse files" or drag & drop your CSV/Excel file
   - File will be analyzed automatically

3. **Review Data Preview**
   - System will show detected columns and data format
   - Verify timestamps and weather parameters are recognized

4. **Import the Data**
   - Click "Process and Import Historical Data"
   - System will map your data to weather parameters
   - Duplicate checking prevents data conflicts

## Expected CSV Format

Your Smart Life export might look like:

```csv
Timestamp,Temperature,Humidity,Pressure,Wind Speed
2024-01-01 08:00,22.5,65,1013.2,2.3
2024-01-01 08:05,22.7,64,1013.1,2.1
2024-01-01 08:10,22.9,63,1013.0,1.8
```

**The system supports various formats:**
- Different timestamp formats (YYYY-MM-DD, MM/DD/YYYY, etc.)
- Different column names (temp, temperature, humid, humidity, etc.)
- Multiple units (Celsius/Fahrenheit, different pressure units)

## Troubleshooting

### If Smart Life App Doesn't Have Export:

1. **Check App Version** - Update to latest version
2. **Look in Different Sections** - Export might be in device settings
3. **Contact Tuya Support** - Ask about data export feature
4. **Screenshot Method** - Take screenshots and we can help extract data

### If CSV Import Fails:

1. **Check File Format** - Ensure it's CSV or Excel
2. **Verify Timestamps** - Data needs timestamp column
3. **Check Column Names** - Should include weather parameters
4. **File Size** - Very large files might need to be split

## What Happens After Import

Once imported successfully:
- Historical data appears in your dashboard charts
- Trend analysis includes imported data
- Combined with automatic collection (288 readings/day going forward)
- Complete weather monitoring with months/years of history

## Support

If you need help finding the export feature or importing data:
- Share screenshots of your Smart Life app
- Upload your CSV file to see analysis results
- Your dashboard will guide you through any format issues