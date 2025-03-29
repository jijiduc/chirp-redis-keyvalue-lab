#!/usr/bin/env python3
"""
Script to launch the Chirp application
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.app.chirp_app import ChirpApp

if __name__ == "__main__":
    # Handle arguments for Redis configuration
    import argparse
    
    parser = argparse.ArgumentParser(description="Launch the Chirp application")
    parser.add_argument("--host", default="localhost", help="Redis host (default: localhost)")
    parser.add_argument("--port", type=int, default=6379, help="Redis port (default: 6379)")
    parser.add_argument("--db", type=int, default=0, help="Redis database (default: 0)")
    
    args = parser.parse_args()
    
    # Create and run the application
    app = ChirpApp(host=args.host, port=args.port, db=args.db)
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e} 🔍")