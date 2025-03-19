#!/usr/bin/env python
"""
Run script for the AttendMax API server
"""
from dotenv import load_dotenv
import os
import sys
from app import app
from db_init import init_db

# Load environment variables
load_dotenv()

if __name__ == '__main__':
    # Check for command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == '--init-db':
            # Initialize database with sample data
            print("Initializing database with sample data...")
            init_db()
            # Exit after initializing database if --init-only flag is provided
            if len(sys.argv) > 2 and sys.argv[2] == '--init-only':
                print("Database initialization complete. Exiting...")
                sys.exit(0)
    
    # Get port from environment or use default
    port = int(os.environ.get('PORT', 5000))
    
    print(f"Starting AttendMax API server on port {port}...")
    print(f"MongoDB URI: {os.environ.get('MONGO_URI', 'mongodb://localhost:27017/attendmax')}")
    print("API Documentation: http://localhost:{port}/")
    print("Press Ctrl+C to stop the server")
    
    # Run the app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=(os.environ.get('DEBUG', 'False').lower() in ('true', '1', 't'))
    ) 