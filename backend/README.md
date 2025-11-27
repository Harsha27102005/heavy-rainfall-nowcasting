# Heavy Rainfall Nowcasting Backend

This is the backend API for the Heavy Rainfall Nowcasting system.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Start MongoDB:**
   Make sure MongoDB is running on `localhost:27017`

3. **Start the server:**
   ```bash
   python start_server.py
   ```
   
   The server will start on `http://127.0.0.1:8000`

## Testing

To test the authentication endpoints:

```bash
python test_auth.py
```

## API Endpoints

- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user info
- `GET /nowcast/{forecast_time}` - Get nowcasting predictions
- `GET /warnings/active` - Get active warnings
- `POST /upload/` - Upload radar data files

## API Documentation

Once the server is running, visit:
- `http://127.0.0.1:8000/docs` - Interactive API documentation
- `http://127.0.0.1:8000/redoc` - Alternative API documentation

## Troubleshooting

### Registration Issues

If you're having trouble with registration:

1. **Check MongoDB connection:**
   ```bash
   python test_mongodb.py
   ```

2. **Check server logs** for any error messages

3. **Verify the server is running** on the correct port

4. **Test the endpoints** using the test script:
   ```bash
   python test_auth.py
   ```

### Common Issues

- **Port already in use:** Change the port in `start_server.py`
- **MongoDB not running:** Start MongoDB service
- **Import errors:** Make sure you're running from the backend directory 