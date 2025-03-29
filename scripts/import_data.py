#!/usr/bin/env python3
"""
Script to import Twitter data into Redis
"""

import os
import sys
import json
import argparse
from tqdm import tqdm

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.redis_model import ChirpRedisModel

def import_data(file_path, host='localhost', port=6379, db=0, limit=None):
    """
    Import data from a JSON file into Redis
    
    Args:
        file_path (str): Path to the JSON file containing tweets
        host (str): Redis host
        port (int): Redis port
        db (int): Redis database
        limit (int, optional): Maximum number of tweets to import
    """
    # Initialize Redis model
    model = ChirpRedisModel(host=host, port=port, db=db)
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ Error: The file {file_path} does not exist.")
        return
    
    # Load JSON data
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            tweets = json.load(f)
    except json.JSONDecodeError:
        # Try to read line by line if the file is not a JSON array
        print("🔄 Not a JSON array, trying line-by-line parsing...")
        tweets = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        tweet = json.loads(line)
                        tweets.append(tweet)
                    except json.JSONDecodeError:
                        continue
    
    # Limit the number of tweets if necessary
    if limit and limit > 0:
        print(f"🔍 Limiting import to {limit} tweets")
        tweets = tweets[:limit]
    
    # Filter English tweets
    english_tweets = [tweet for tweet in tweets if tweet.get('lang') == 'en']
    print(f"🌐 Total number of English tweets: {len(english_tweets)}")
    
    # Import tweets into Redis with a progress bar
    imported_count = 0
    users_seen = set()
    
    print("🚀 Importing tweets into Redis...")
    for tweet in tqdm(english_tweets, desc="⏳ Importing"):
        try:
            # Import the chirp (which also imports the user)
            model.import_chirp(tweet)
            
            # Track imported users
            user_id = str(tweet['user']['id'])
            if user_id not in users_seen:
                users_seen.add(user_id)
            
            imported_count += 1
        except KeyError as e:
            # Ignore tweets with missing data
            print(f"⚠️ Warning: Missing data in a tweet - {e}")
            continue
        except Exception as e:
            print(f"❌ Error importing a tweet: {e}")
            continue
    
    print(f"\n✅ Import completed!")
    print(f"📊 Tweets imported: {imported_count}")
    print(f"👥 Users imported: {len(users_seen)}")
    
    # Display some statistics
    print("\n📈 Statistics:")
    print(f"- 💬 Total number of chirps: {model.redis.zcard('chirps:timeline')}")
    print(f"- 👤 Total number of users: {len(model.redis.keys('users:*'))}")
    
    # Display top 5 users with most followers
    top_followers = model.get_top_users_by_followers(5)
    print("\n🏆 Top 5 users with the most followers:")
    for i, user in enumerate(top_followers, 1):
        print(f"{i}. @{user['username']} - {user['follower_count']} followers")
    
    # Display 5 latest chirps
    latest_chirps = model.get_latest_chirps(5)
    print("\n🕒 5 latest chirps:")
    for chirp in latest_chirps:
        print(f"- @{chirp['username']}: {chirp['text'][:50]}...")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import Twitter data into Redis")
    parser.add_argument("file", help="Path to the JSON file containing tweets")
    parser.add_argument("--host", default="localhost", help="Redis host (default: localhost)")
    parser.add_argument("--port", type=int, default=6379, help="Redis port (default: 6379)")
    parser.add_argument("--db", type=int, default=0, help="Redis database (default: 0)")
    parser.add_argument("--limit", type=int, help="Maximum number of tweets to import")
    parser.add_argument("--reset", action="store_true", help="Reset the database before importing")
    
    args = parser.parse_args()
    
    # Reset database if requested
    if args.reset:
        model = ChirpRedisModel(host=args.host, port=args.port, db=args.db)
        print("🧹 Resetting Redis database...")
        model.reset_db()
    
    # Import data
    import_data(args.file, args.host, args.port, args.db, args.limit)