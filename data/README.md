# Test Data and Scripts

This folder contains test data and scripts for the Heavy Rainfall Nowcasting system.

## Files

- `sample_radar_data.csv` - Sample radar data for model training
- `sample_training_labels.csv` - Sample training labels for model training
- `test_notifications.py` - Script to test SMS and email notifications
- `test_upload_fix.py` - Script to test upload functionality and dynamic contact info

## How to Run test_notifications.py

### Step 1: Start the Backend Server
```bash
cd backend
python main.py
```

### Step 2: Update Contact Information
Edit `test_notifications.py` and change these lines:
```python
ADMIN_EMAIL = "your-email@example.com"  # Change this to your email
ADMIN_PHONE = "+1234567890"  # Change this to your phone number
```

### Step 3: Run the Test Script
```bash
cd data
python test_notifications.py
```

### Step 4: Check Results
The script will:
1. ✅ Check if backend is running
2. 📢 Create 3 test warnings (CC, MCC, SLP types)
3. 📋 Check active warnings
4. 📬 Check notifications
5. 📧 Send email notifications (if configured)
6. 📱 Send SMS notifications (if configured)

### Expected Output
```
🚀 Testing Heavy Rainfall Nowcasting Notification System
============================================================
📧 Admin Email: your-email@example.com
📱 Admin Phone: +1234567890
🌐 Backend URL: http://localhost:8000

✅ Backend is running

📢 Creating test warnings to trigger notifications...

--- Test Warning 1 ---
Cell ID: test_cell_001
MCS Type: CC
Rain Rate: 45.8 mm/h
✅ Warning created successfully
Warning ID: 507f1f77bcf86cd799439011

--- Test Warning 2 ---
Cell ID: test_cell_002
MCS Type: MCC
Rain Rate: 58.9 mm/h
✅ Warning created successfully

--- Test Warning 3 ---
Cell ID: test_cell_003
MCS Type: SLP
Rain Rate: 73.8 mm/h
✅ Warning created successfully

📋 Checking active warnings...
✅ Found 3 active warnings

📬 Checking notifications...
✅ Found 3 notifications

🎯 Test completed!
```

## Troubleshooting

### If Backend is Not Running
```
❌ Cannot connect to backend. Make sure it's running on http://localhost:8000
```
**Solution**: Start the backend server first

### If No Notifications Received
1. Check your `.env` file has correct SMTP/Twilio credentials
2. Verify email and phone number in the script
3. Check spam folder for emails
4. Ensure Twilio account is active for SMS

### Environment Variables Needed
```bash
# Email (SMTP)
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# SMS (Twilio)
TWILIO_ACCOUNT_SID=your-account-sid
TWILIO_AUTH_TOKEN=your-auth-token
TWILIO_PHONE_NUMBER=+1234567890

# Notifications
ENABLE_EMAIL_NOTIFICATIONS=true
ENABLE_SMS_NOTIFICATIONS=true
```

## Testing Upload Functionality

Run the upload test script:
```bash
python test_upload_fix.py
```

This will test:
- ✅ Upload functionality bug fix
- 📞 Dynamic contact information feature
- 📬 Notification system with dynamic contact info 