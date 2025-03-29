#!/usr/bin/env python3
"""
Script to process JSONL tweet files compressed in bz2 format
"""

import json
import bz2
import os
from pathlib import Path

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

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        input_dir = sys.argv[1]
    else:
        input_dir = "./data/twitter_data"
    
    output_dir = "./data/processed"
    process_jsonl_bz2_files(input_dir, output_dir)