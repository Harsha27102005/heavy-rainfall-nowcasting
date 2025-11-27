# India Monsoon Sample Dataset

This directory contains sample data for testing the Heavy Rainfall Nowcasting system with realistic Indian monsoon conditions.

## 📁 Files Included

- `india_radar_data.csv` - Radar data for storm cells over Mumbai Metropolitan Region
- `india_training_labels.csv` - Training labels for heavy rainfall events
- `india_storm_cells.geojson` - Geographic data for storm cell locations

## 🌧️ Dataset Characteristics

### Location
- **Primary Region**: Mumbai Metropolitan Region, India
- **Coordinates**: 19.0760° N, 72.8777° E (Mumbai)
- **Coverage**: Mumbai, Thane, Pune areas
- **Weather**: Monsoon Season (July)

### Storm Cells
1. **MUMBAI_MONSOON_01** (MCC - Mesoscale Convective Complex)
   - Rainfall: 95.7 mm/h (Heavy)
   - Location: Mumbai
   - Warning Level: Red

2. **THANE_VERY_HEAVY_001** (SLD - Squall Line)
   - Rainfall: 125.6 mm/h (Very Heavy)
   - Location: Thane
   - Warning Level: Red

3. **PUNE_MODERATE_001** (CC - Convective Cell)
   - Rainfall: 65.4 mm/h (Moderate)
   - Location: Pune
   - Warning Level: Orange

## 📊 Data Statistics

- **Radar Records**: 144 (48 hours × 3 cells)
- **Training Labels**: 15 (5 variations per event)
- **Heavy Rainfall Events**: 10
- **Warning Triggers**: 10
- **Time Period**: 48 hours of monsoon data

## 🚀 How to Use

### 1. Start the Backend Server
```bash
cd backend
python main.py
```

### 2. Start the Frontend Server
```bash
cd frontend
npm start
```

### 3. Access the Training Page
- Open your browser to `http://localhost:3000`
- Login with your credentials
- Navigate to the "Model Training" page

### 4. Upload the Sample Data
1. **Upload Radar Data**:
   - Click "Upload Radar Data"
   - Select `india_radar_data.csv`
   - Click "Upload Radar Data"

2. **Upload Training Labels**:
   - Click "Upload Training Labels"
   - Select `india_training_labels.csv`
   - Click "Upload Labels"

### 5. Start Model Training
- Click "Start Model Training"
- Wait for training to complete (simulated 10 seconds)

### 6. Start Real-time Monitoring
- Click "Start Real-time Monitoring"
- Provide your email and phone number
- Click "Start Monitoring"

## 🎯 Expected Results

### Dashboard Display
- Interactive map showing storm cells over India
- Red warning areas for heavy rainfall
- Real-time updates every 5 minutes

### Notifications
- **Email Alerts**: Detailed warnings sent to your email
- **SMS Alerts**: Concise warnings sent to your phone
- **Warning Levels**: Red for heavy, Orange for moderate

### Sample Notifications

#### Email Example:
```
Subject: ⚠️ HEAVY RAINFALL WARNING

HEAVY RAINFALL WARNING

Cell ID: MUMBAI_MONSOON_01
MCS Type: MCC
Forecast Time: 30 minutes
Predicted Top 10% Rain Rate: 95.7 mm/h
Predicted Timestamp: 2024-07-15 14:30:00
Message: Heavy rainfall warning: Expected rainfall intensity exceeding 90 mm/h in the next 30 minutes over Mumbai region. Risk of flooding in low-lying areas.

This warning was issued at: 2024-07-15 12:25:19 UTC

Please take necessary precautions and monitor the situation.

---
Heavy Rainfall Nowcasting System
```

#### SMS Example:
```
⚠️ HEAVY RAINFALL WARNING
Cell: MUMBAI_MONSOON_01
Type: MCC
Rain Rate: 95.7mm/h
Time: 30min
Heavy rainfall warning: Expected rainfall intensity exceeding 90 mm/h in the next 30 minutes over Mumbai region. Risk of flooding in low-lying areas.
```

## 🔧 Configuration

### For Real Notifications
To receive actual email and SMS notifications, set these environment variables:

```bash
# Email (Gmail)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-twilio-sid
TWILIO_AUTH_TOKEN=your-twilio-token
TWILIO_PHONE_NUMBER=your-twilio-number
```

### For Testing (Current Setup)
The system currently uses mock notifications that log to the console instead of sending real emails/SMS.

## 📈 Data Quality

### Realistic Features
- ✅ Monsoon rainfall patterns
- ✅ Indian geographic coordinates
- ✅ Realistic storm cell types (MCC, SLD, CC)
- ✅ Temporal variations
- ✅ Multiple intensity levels
- ✅ Geographic distribution

### Training Data
- ✅ 144 radar observations
- ✅ 15 labeled events
- ✅ Heavy rainfall thresholds (>70 mm/h)
- ✅ Warning trigger conditions
- ✅ Geographic boundaries

## 🛠️ Troubleshooting

### Common Issues
1. **Training page not loading**: Check if backend server is running
2. **Upload fails**: Ensure CSV files are in correct format
3. **No notifications**: Check console logs for mock notifications
4. **Map not showing**: Verify GeoJSON data is properly formatted

### Database Check
```bash
# Check if warnings are stored
python -c "from app.database import sync_warnings_collection; print('Warnings:', sync_warnings_collection.count_documents({}))"

# Check if notifications are stored
python -c "from app.database import sync_notifications_collection; print('Notifications:', sync_notifications_collection.count_documents({}))"
```

## 📞 Support

If you encounter any issues:
1. Check the console logs for error messages
2. Verify all servers are running
3. Ensure database connection is working
4. Check file permissions for uploads

---

**Note**: This is sample data for demonstration purposes. For production use, replace with real radar data and adjust thresholds according to your specific requirements.



