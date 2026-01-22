#!/usr/bin/env python3
"""
Debug server script with built-in breakpoints
"""
import os
import sys
import pdb

# Add backend to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Set debug mode
os.environ['DEBUG'] = 'True'

if __name__ == "__main__":
    # Set trace for debugging
    pdb.set_trace()
    
    # Import and run uvicorn
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        debug=True,
        log_level="debug"
    )
