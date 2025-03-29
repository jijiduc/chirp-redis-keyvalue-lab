#!/usr/bin/env python3
"""
Script to process JSONL tweet files compressed in bz2 format
Added functionality to generate sample data for testing
"""

import json
import bz2
import os
import sys
import argparse
import random
from pathlib import Path
from datetime import datetime, timedelta
import time

def generate_sample_data(num_users=20, tweets_per_user=5):
    """Generate synthetic Twitter data for testing"""
    print(f"🔧 Generating sample data with {num_users} users and {tweets_per_user} tweets per user...")
    
    users = []
    tweets = []
    
    # Generate users
    for i in range(1, num_users + 1):
        user_id = 1000000 + i
        user = {
            "id": user_id,
            "name": f"Test User {i}",
            "screen_name": f"user{i}",
            "followers_count": random.randint(10, 1000),
            "friends_count": random.randint(10, 500),
            "statuses_count": random.randint(50, 2000),
            "created_at": "Mon Apr 01 12:00:00 +0000 2025",
        }
        users.append(user)
    
    # Generate tweets
    current_time = time.time()
    for user in users:
        for j in range(tweets_per_user):
            tweet_time = current_time - random.randint(0, 30*24*60*60)  # Random time within last 30 days
            tweet = {
                "id": int(tweet_time * 1000),  # Use timestamp as ID
                "text": f"This is test tweet {j} from {user['screen_name']}. #testing #chirp",
                "user": user,
                "created_at": (datetime.now() - timedelta(seconds=current_time-tweet_time)).strftime("%a %b %d %H:%M:%S +0000 %Y"),
                "timestamp_ms": str(int(tweet_time * 1000)),
                "favorite_count": random.randint(0, 50),
                "retweet_count": random.randint(0, 20),
                "lang": "en"
            }
            tweets.append(tweet)
    
    return tweets

def process_jsonl_bz2_files(input_dir, output_dir):
    """Process JSONL files compressed in bz2 and extract English tweets"""
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Find all .bz2 files
    bz2_files = list(Path(input_dir).glob("*.json.bz2"))
    print(f"🔍 Found {len(bz2_files)} .bz2 files")
    
    if not bz2_files:
        print(f"❌ No .bz2 files found in {input_dir}")
        return
    
    # Process each file
    all_english_tweets = []
    for file_path in bz2_files:
        print(f"⏳ Processing {file_path}...")
        try:
            english_tweets_in_file = 0
            
            # Open the bz2 file and read line by line
            with bz2.open(file_path, 'rt', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if not line:  # Ignore empty lines
                        continue
                    
                    try:
                        # Parse each line as an independent JSON object
                        tweet = json.loads(line)
                        
                        # Check if the tweet is in English
                        if tweet.get('lang') == 'en':
                            all_english_tweets.append(tweet)
                            english_tweets_in_file += 1
                    except json.JSONDecodeError as je:
                        print(f"  ⚠️ JSON decoding error in {file_path}: {je}")
                        continue
            
            print(f"  📊 {english_tweets_in_file} English tweets found in {file_path.name}")
        
        except Exception as e:
            print(f"❌ Error processing {file_path}: {e}")
    
    # Save results
    print(f"📈 Total: {len(all_english_tweets)} English tweets")
    
    if all_english_tweets:
        # Save all tweets to a file instead of just a sample
        all_tweets_file = os.path.join(output_dir, "english_tweets.json")
        
        with open(all_tweets_file, 'w', encoding='utf-8') as f:
            json.dump(all_english_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"💾 All {len(all_english_tweets)} English tweets saved in {all_tweets_file}")
    else:
        print("📭 No English tweets found to save.")

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Process Twitter data or generate sample data")
    parser.add_argument("input_dir", nargs="?", default="./data/twitter_data", 
                        help="Directory containing .bz2 files (default: ./data/twitter_data)")
    parser.add_argument("--output-dir", default="./data/processed", 
                        help="Output directory for processed files (default: ./data/processed)")
    parser.add_argument("--generate-sample", action="store_true", 
                        help="Generate sample data instead of processing files")
    parser.add_argument("--users", type=int, default=20, 
                        help="Number of users in sample data (default: 20)")
    parser.add_argument("--tweets", type=int, default=5, 
                        help="Tweets per user in sample data (default: 5)")
    
    args = parser.parse_args()
    
    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)
    
    if args.generate_sample:
        # Generate sample data
        sample_tweets = generate_sample_data(args.users, args.tweets)
        
        # Save sample data
        sample_file = os.path.join(args.output_dir, "sample_english_tweets.json")
        with open(sample_file, 'w', encoding='utf-8') as f:
            json.dump(sample_tweets, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Generated {len(sample_tweets)} sample tweets saved in {sample_file}")
    else:
        # Process real data files
        process_jsonl_bz2_files(args.input_dir, args.output_dir)

if __name__ == "__main__":
    main()