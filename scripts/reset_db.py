#!/usr/bin/env python3
"""
Script to reset the Redis database
"""

import os
import sys
import argparse

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.redis_model import ChirpRedisModel

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Reset the Redis database")
    parser.add_argument("--host", default="localhost", help="Redis host (default: localhost)")
    parser.add_argument("--port", type=int, default=6379, help="Redis port (default: 6379)")
    parser.add_argument("--db", type=int, default=0, help="Redis database (default: 0)")
    parser.add_argument("--force", action="store_true", help="Do not ask for confirmation")
        
    args = parser.parse_args()
    
    # Ask for confirmation unless --force is used
    if not args.force:
        confirm = input("⚠️  Are you sure you want to reset the Redis database? (y/n) ")
        if confirm.lower() != 'y':
            print("🛑 Operation cancelled.")
            sys.exit(0)

    # Reset the database
    print("🧹 Cleaning up Redis database...")
    model = ChirpRedisModel(host=args.host, port=args.port, db=args.db)
    model.reset_db()
    print("✅ Redis database successfully reset.")