# Heavy Rainfall Test Datasets

## 📋 Overview
This directory contains **test datasets with extreme rainfall values** designed to trigger heavy rainfall email alerts in your nowcasting system.

## 📁 Test Files Created

### 1. `test_heavy_rainfall_radar.csv`
Radar data with **extremely high rainfall rates** (155-347 mm/h) for 5 major Indian cities:
- **Delhi** - MCC type storms
- **Mumbai** - SLD type storms  
- **Kolkata** - CC type storms
- **Chennai** - MCC type storms
- **Bangalore** - SLD type storms

**Time Range**: 2025-11-22 12:00:00 to 18:00:00 (7 hours of data)

### 2. `test_heavy_rainfall_labels.csv`
Corresponding labels with:
- `is_warning_triggered = True` for all events
- `is_critical_event = True` for most events
- `warning_level = red` for all events
- Top 10% rainfall rates: **195-281 mm/h** (well above typical thresholds)

### 3. `test_heavy_rainfall_cells.geojson`
GeoJSON file with polygon boundaries for all 5 storm cells.

---

## 🚀 How to Test Email Alerts

### Step 1: Configure Email Settings
Make sure your `.env` file in the `backend` directory has valid email credentials:

```env
# Email Configuration (Gmail example)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Notification Settings
ENABLE_EMAIL_NOTIFICATIONS=true
HEAVY_RAINFALL_THRESHOLD_MM_H=90.0
```

> **Note**: For Gmail, you need to use an [App Password](https://support.google.com/accounts/answer/185833), not your regular password.

### Step 2: Start the Backend Server
```bash
cd backend
python -m uvicorn app.main:app --reload
```

Wait for the message: `Application startup complete. Scheduler running.`

### Step 3: Upload Test Data

#### Option A: Using the Frontend (Recommended)
1. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```
2. Navigate to the **Training** page
3. Upload the test files:
   - **Radar Data**: `test_heavy_rainfall_radar.csv`
   - **Labels**: `test_heavy_rainfall_labels.csv`
   - **GeoJSON**: `test_heavy_rainfall_cells.geojson`

#### Option B: Using API Directly
```bash
curl -X POST "http://localhost:8000/training/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "radar_file=@data/test_heavy_rainfall_radar.csv" \
  -F "labels_file=@data/test_heavy_rainfall_labels.csv" \
  -F "geojson_file=@data/test_heavy_rainfall_cells.geojson"
```

### Step 4: Trigger Predictions
The system should automatically process the data. You can also manually trigger predictions:

```bash
curl -X POST "http://localhost:8000/training/trigger-nowcast" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 5: Check for Email Alerts
You should receive email alerts for:
- ✉️ **Delhi** - Critical rainfall (225-260 mm/h)
- ✉️ **Mumbai** - Extreme rainfall (240-281 mm/h)
- ✉️ **Kolkata** - Severe rainfall (205-243 mm/h)
- ✉️ **Chennai** - Heavy rainfall (215-255 mm/h)
- ✉️ **Bangalore** - Monsoon rainfall (195-232 mm/h)

---

## 📊 Expected Behavior

### What Should Happen:
1. ✅ System processes the uploaded radar data
2. ✅ ML models make predictions (if trained)
3. ✅ System detects rainfall rates **above threshold** (90 mm/h)
4. ✅ Warnings are created in the database
5. ✅ **Email notifications are sent** to configured addresses
6. ✅ Warnings appear on the Dashboard

### Email Content Example:
```
Subject: ⚠️ Heavy Rainfall Warning - MUMBAI_EXTREME_02

Heavy rainfall predicted for storm cell 'MUMBAI_EXTREME_02' (SLD type) 
in 30 minutes!

Predicted Top 10% Mean Rain Rate: 281.3 mm/h
Expected at: 2025-11-22 17:00:00 UTC

Location: Mumbai (19.0760°N, 72.8777°E)
Severity: CRITICAL
Warning Level: RED
```

---

## 🔍 Verification Steps

### 1. Check Backend Logs
Look for messages like:
```
*** WARNING ISSUED: Heavy rainfall predicted for storm cell 'DELHI_CRITICAL_01'...
Warning stored in DB with ID: 507f1f77bcf86cd799439011
Email notification sent to: your-email@gmail.com
```

### 2. Check Database
Query the warnings collection:
```javascript
db.warnings.find({ is_active: true }).pretty()
```

### 3. Check Dashboard
- Navigate to the Dashboard page
- You should see **active alerts** for all 5 cities
- Map should show storm cell markers

---

## 🛠️ Troubleshooting

### No Email Received?
1. **Check spam folder** - Automated emails often go to spam
2. **Verify SMTP credentials** - Test with a simple email script
3. **Check backend logs** - Look for email sending errors
4. **Verify threshold** - Make sure `HEAVY_RAINFALL_THRESHOLD_MM_H` is below 195 mm/h
5. **Check notification service** - Ensure `ENABLE_EMAIL_NOTIFICATIONS=true`

### Models Not Trained?
If you see: `Models not trained yet. Skipping prediction cycle.`

Train the models first:
```bash
curl -X POST "http://localhost:8000/training/train" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### No Warnings Created?
- Check if predictions are being made
- Verify rainfall values are above threshold
- Check database connection
- Review `data_ingestion_service.py` logs

---

## 📝 Data Characteristics

### Rainfall Intensity Levels:
- **Top 10% Mean RR**: 195-281 mm/h (EXTREME)
- **Mean RR**: 155-235 mm/h (VERY HIGH)
- **Max RR**: 235-347 mm/h (CATASTROPHIC)

### Comparison to Thresholds:
- Typical heavy rainfall threshold: **90 mm/h**
- These test values: **195-281 mm/h** (2-3x threshold)
- **Guaranteed to trigger alerts!** ✅

---

## 🎯 Success Criteria

Your test is successful if:
- ✅ You receive **at least 5 email alerts** (one per city)
- ✅ Warnings appear in the **Dashboard**
- ✅ Database contains **active warnings**
- ✅ Backend logs show **"Email notification sent"**

---

## 📧 Need Help?

If you're still not receiving emails after following all steps:
1. Check your email provider's security settings
2. Try a different email address
3. Review the `notification_service.py` implementation
4. Check if FastAPI-Mail is configured correctly

---

## 🔄 Clean Up After Testing

To remove test warnings from the database:
```javascript
db.warnings.deleteMany({ cell_id: { $in: [
  "DELHI_CRITICAL_01",
  "MUMBAI_EXTREME_02", 
  "KOLKATA_SEVERE_03",
  "CHENNAI_HEAVY_04",
  "BANGALORE_MONSOON_05"
]}})
```

---

**Good luck with your testing! 🌧️📧**
