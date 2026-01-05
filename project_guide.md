# TCS Prime Interview Guide: Heavy Rainfall Nowcasting System

This guide provides a comprehensive overview of the Heavy Rainfall Nowcasting System, its architecture, workflow, APIs, and the challenges faced during development.

---

## 1. Project Overview
The **Heavy Rainfall Nowcasting System** is a real-time weather monitoring and prediction platform. It uses radar data and machine learning models to predict heavy rainfall events (nowcasting) and issue early warnings to users.

### Key Features:
- **Real-time Nowcasting**: Predicts rainfall intensity for the next 30 and 60 minutes.
- **Storm Cell Tracking**: Identifies and monitors individual storm cells on an interactive map.
- **Early Warning System**: Automatically generates and sends email alerts for high-risk events.
- **Crowdsourcing**: Allows users to report local rainfall conditions to validate predictions.
- **Admin Dashboard**: For model training and system monitoring.

### Technology Stack:
- **Frontend**: React.js, Redux Toolkit, Leaflet.js (for maps), Tailwind CSS (Glassmorphism UI).
- **Backend**: FastAPI (Python), Motor (Async MongoDB driver).
- **Database**: MongoDB (Local and Atlas).
- **Machine Learning**: TensorFlow (1D CNN), Scikit-learn (Lasso Regression), Joblib.
- **Communication**: FastMail (SMTP) for email notifications.

---

## 2. Full Workflow

### Step 1: Data Ingestion
The system periodically fetches radar data (simulated or real-time) from a specified path.
- **Service**: `DataIngestionService`
- **Logic**: Reads radar composite images and identifies "storm cells" based on reflectivity thresholds.

### Step 2: Feature Extraction & Transformation
For each identified storm cell, the system derives several meteorological variables:
- **Radar Variables**: Reflectivity, VIL (Vertically Integrated Liquid), Echo Top, MaxZ, etc.
- **Topographic Features**: Elevation, slope, aspect, distance to sea.
- **Data Transformation**: To improve ML performance, variables are transformed (e.g., log-transform for VIL and Area, scaling for Reflectivity) as per meteorological standards.
- **MCS Categorization**: Categorizes the cell into types like Squall Line, MCC (Mesoscale Convective Complex), etc.

### Step 3: Machine Learning Prediction
The system uses two types of models for each cell:
1.  **Classification (1D CNN)**: Predicts *if* a storm cell will persist and cause heavy rain in 30/60 minutes.
2.  **Regression (ANN/Lasso)**: Predicts the *intensity* (Mean Rain Rate and Top 10% Rain Rate) of the rainfall.

### Step 4: Early Warning Generation
If the predicted **Top 10% Rain Rate** exceeds a threshold (e.g., 16 mm/h):
- A warning is generated and stored in MongoDB.
- An email alert is sent via `NotificationService`.
- The warning is displayed in real-time on the frontend dashboard.

### Step 5: Visualization & Interaction
- **Dashboard**: Displays storm cells as markers and circles on a map. High-risk cells are colored red.
- **Crowdsourcing**: Users submit reports which are stored in the database for future model validation.

---

## 3. API Documentation

### Authentication (`/auth`)
- `POST /auth/register`: Initiates registration and sends OTP to email.
- `POST /auth/register/verify`: Verifies OTP and creates the user account.
- `POST /auth/login`: Authenticates user and returns a JWT token.
- `GET /auth/me`: Retrieves current user profile.
- `POST /auth/forgot-password`: Sends password reset OTP.
- `POST /auth/reset-password`: Resets password using OTP.

### Nowcasting (`/nowcast`)
- `GET /nowcast/{forecast_time}`: Retrieves predictions for '30min' or '60min'.

### Warnings (`/warnings`)
- `GET /warnings/active`: Fetches all currently active heavy rainfall warnings.

### Crowdsourcing (`/crowdsource`)
- `POST /crowdsource/report`: Submits a user rainfall report.
- `GET /crowdsource/reports`: Retrieves recent crowdsourced reports.

---

## 4. Problems Encountered & Solutions

| Problem | Solution |
| :--- | :--- |
| **MongoDB SSL Handshake Error** | Initially occurred during deployment. Solved by reverting to a local MongoDB instance for development and later configuring IP whitelisting for MongoDB Atlas. |
| **Invalid LatLng Object on Map** | Frontend crashed when displaying storm cells. Fixed by correctly extracting latitude/longitude from the GeoJSON `predicted_location` object in `Dashboard.js`. |
| **Email Notifications Not Sending** | The `NotificationService` wasn't being triggered in test scripts. Updated `insert_test_warnings.py` to explicitly call the notification service. |
| **OTP Verification Logic Flaw** | Users were being registered even if OTP verification failed. Refactored `auth.py` to ensure user creation only happens *after* successful OTP validation. |
| **UI Readability Issues** | Text was hard to read against the background. Applied a consistent glassmorphism theme with white text, increased brightness, and backdrop filters. |

---

## 5. Potential Interview Questions (Q&A)

**Q: Why did you choose FastAPI over Flask or Django?**
**A:** FastAPI is asynchronous by default, making it highly performant for I/O-bound tasks like database queries and sending emails. It also provides automatic Swagger documentation, which sped up development.

**Q: How does your ML model handle different types of storm cells?**
**A:** We use a categorization logic to identify the MCS (Mesoscale Convective System) type. We then load specific models trained for that type (e.g., Squall Line vs. MCC) to improve prediction accuracy.

**Q: How do you handle real-time updates on the Dashboard?**
**A:** The frontend uses a `setInterval` hook to poll the `/nowcast` and `/warnings/active` endpoints every 5 minutes, ensuring the map stays updated with the latest predictions.

**Q: What is the significance of the "Top 10% Rain Rate"?**
**A:** While the Mean Rain Rate gives an average, the Top 10% represents the most intense part of the storm, which is a better indicator of potential flooding or flash flood risks.

**Q: How do you secure your APIs?**
**A:** We use JWT (JSON Web Tokens) for authentication. Sensitive endpoints (like model training) are protected by an `admin_user` dependency that checks the user's role.
