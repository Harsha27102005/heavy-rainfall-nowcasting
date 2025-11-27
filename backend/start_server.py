#!/usr/bin/env python3
"""
Startup script for the Heavy Rainfall Nowcasting API server.
This ensures the server runs from the correct directory.
"""

import os
import sys
import uvicorn

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("Starting Heavy Rainfall Nowcasting API server...")
    print(f"Working directory: {os.getcwd()}")
#!/usr/bin/env python3
"""
Startup script for the Heavy Rainfall Nowcasting API server.
This ensures the server runs from the correct directory.
"""

import os
import sys
import uvicorn

# Add the backend directory to the Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

if __name__ == "__main__":
    print("Starting Heavy Rainfall Nowcasting API server...")
    print(f"Working directory: {os.getcwd()}")
    print(f"Backend directory: {backend_dir}")
    
    # Change to the backend directory
    os.chdir(backend_dir)
    
    # Start the server
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )