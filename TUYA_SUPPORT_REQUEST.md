# Tuya Support Request Template

## Issue Summary
I am experiencing persistent "sign invalid" errors (code 1004) when attempting to access Tuya Cloud APIs for my weather station device, despite having an active Trial Edition subscription and proper credentials.

## Technical Details

**Project Information:**
- Project Name: [Your project name]
- Access ID: fxtdf9uy9uef3qv9nege
- Device ID: bf5f5736feb7d67046gdkw
- Device Type: GARNI 925T Weather Station
- Subscription: IoT Core Trial Edition (Active)

**Error Details:**
- Error Code: 1004
- Error Message: "sign invalid"
- Occurs on all regional endpoints:
  - https://openapi.tuyaeu.com
  - https://openapi.tuyaus.com  
  - https://openapi.tuyacn.com

**What I've Already Tried:**
1. ✅ Verified I have active IoT Core Trial Edition subscription
2. ✅ Generated fresh Access ID and Access Key credentials multiple times
3. ✅ Tested signature generation using official Tuya documentation methods
4. ✅ Verified device is properly linked to my Tuya Smart app account
5. ✅ Tested with different regional endpoints
6. ✅ Confirmed project was created after May 25, 2021
7. ✅ Verified timestamp and request formatting

**Signature Generation Method Used:**
```
content_hash = SHA256(request_body)
string_to_sign = "GET\n" + content_hash + "\n\n" + full_url
signature_string = access_id + timestamp + string_to_sign
signature = HMAC-SHA256(signature_string, secret_key).upper()
```

**Sample Request Headers:**
```
{
  'client_id': 'fxtdf9uy9uef3qv9nege',
  't': '1753354610112',
  'sign_method': 'HMAC-SHA256',
  'sign': '[generated_signature]',
  'Content-Type': 'application/json'
}
```

## Questions for Support

1. **API Service Subscriptions:** Do I need to subscribe to additional API services beyond IoT Core Trial Edition? If so, which specific services are required for weather station device access?

2. **Account Verification:** Can you verify that my account (Access ID: fxtdf9uy9uef3qv9nege) has proper API permissions enabled?

3. **Regional Endpoint:** Which regional endpoint should I use for my location/project?

4. **Trial Limitations:** Are there any undocumented limitations in the Trial Edition that would cause authentication failures?

5. **Project Configuration:** Can you verify that my project configuration is correct for API access?

## Expected Outcome
I need to be able to authenticate with the Tuya Cloud API to retrieve weather data from my GARNI 925T device for a personal weather monitoring application.

## Urgency
This is blocking development of my weather monitoring system. Any guidance on the correct API service subscriptions or account configuration would be greatly appreciated.

## Additional Information
I am willing to upgrade to a paid plan if the Trial Edition has limitations that prevent API access for weather station devices. Please advise on the minimum required subscription level for this use case.

---

**Contact Information:**
[Your email address]
[Your Tuya account details]