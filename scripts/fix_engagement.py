#!/usr/bin/env python3
"""
Script to add random engagement to existing chirps in Redis
"""

import random
import redis
import sys

def add_engagement_to_chirps():
    """Add random engagement metrics to all existing chirps"""
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Get all chirp keys
    chirp_keys = r.keys("chirp:*")
    
    if not chirp_keys:
        print("No chirps found in the database.")
        return
    
    print(f"Found {len(chirp_keys)} chirps. Adding random engagement...")
    
    # Update each chirp with random engagement
    count = 0
    for key in chirp_keys:
        # Generate random engagement metrics
        likes = random.randint(0, 5000000)
        retweets = random.randint(0, 20000000)
        
        # Update the chirp
        r.hset(key, "favorite_count", likes)
        r.hset(key, "retweet_count", retweets)
        count += 1
        
        # Show progress
        if count % 50 == 0:
            print(f"Updated {count} chirps...")
    
    print(f"✅ Successfully added random engagement to {count} chirps!")
    print("\nNow try viewing the latest chirps again to see the engagement metrics.")

if __name__ == "__main__":
    print("🚀 Adding random engagement metrics to existing chirps...")
    add_engagement_to_chirps()