# Heavy Rainfall Nowcasting System

A real-time heavy rainfall nowcasting system with storm cell prediction and early warnings.

## Project Structure

```
heavy-rainfall-nowcasting/
├── backend/          # FastAPI backend server
├── frontend/         # React frontend application
├── data/            # Data storage
├── ml_models/       # Machine learning models
└── docs/           # Documentation
```

## Quick Start

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd backend
   ```

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start MongoDB:**
   Make sure MongoDB is running on `localhost:27017`

4. **Start the backend server:**
   ```bash
   python start_server.py
   ```
   
   The API will be available at `http://127.0.0.1:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```
   
   The frontend will be available at `http://localhost:3000`

## Testing

### Backend Testing

To test the authentication endpoints:

```bash
cd backend
python test_auth.py
```

### Frontend Testing

The frontend will automatically connect to the backend at `http://127.0.0.1:8000`.

## API Documentation

Once the backend is running, visit:
- `http://127.0.0.1:8000/docs` - Interactive API documentation
- `http://127.0.0.1:8000/redoc` - Alternative API documentation

## Troubleshooting

### Registration Issues

If you're having trouble with user registration:

1. **Check MongoDB connection:**
   ```bash
   cd backend
   python test_mongodb.py
   ```

2. **Test the backend API:**
   ```bash
   cd backend
   python test_auth.py
   ```

3. **Check server logs** for any error messages

4. **Verify both servers are running:**
   - Backend: `http://127.0.0.1:8000`
   - Frontend: `http://localhost:3000`

### Common Issues

- **Port conflicts:** Change ports in the respective configuration files
- **MongoDB not running:** Start MongoDB service
- **Import errors:** Make sure you're running from the correct directory
- **CORS issues:** Check that the frontend URL is in the backend CORS origins

## Features

- **User Authentication:** Register and login users
- **Real-time Nowcasting:** Predict heavy rainfall events
- **Storm Cell Tracking:** Monitor storm cell locations
- **Early Warnings:** Generate and manage weather warnings
- **Data Upload:** Upload radar data files
- **Interactive Dashboard:** Visualize predictions and warnings

## Technology Stack

- **Backend:** FastAPI, MongoDB, TensorFlow, scikit-learn
- **Frontend:** React, Redux Toolkit, Tailwind CSS
- **Database:** MongoDB
- **ML:** TensorFlow, scikit-learn, joblib 