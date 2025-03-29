#!/usr/bin/env python3
"""
Redis Data Model for the Chirp application
"""

import json
import redis
import time
import random
from datetime import datetime

class ChirpRedisModel:
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize the Redis connection"""
        self.redis = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        
    def reset_db(self):
        """Reset the database"""
        self.redis.flushdb()
        print("🗑️ Redis database reset.")
    
    def import_user(self, user_data):
        """
        Import user data into Redis
        
        Args:
            user_data (dict): User data extracted from the tweet
        
        Returns:
            str: ID of the imported user
        """
        user_id = str(user_data['id'])
        
        # Check if the user already exists
        if self.redis.exists(f"users:{user_id}"):
            # Update counters only
            self.redis.hset(f"users:{user_id}", "follower_count", user_data['followers_count'])
            self.redis.hset(f"users:{user_id}", "following_count", user_data['friends_count'])
            self.redis.hset(f"users:{user_id}", "chirp_count", user_data['statuses_count'])
        else:
            # Create a new user
            user_hash = {
                "username": user_data['screen_name'],
                "name": user_data['name'],
                "follower_count": user_data['followers_count'],
                "following_count": user_data['friends_count'],
                "chirp_count": user_data['statuses_count'],
                "created_at": user_data['created_at'],
                "profile_image": user_data.get('profile_image_url_https', '')
            }
            self.redis.hset(f"users:{user_id}", mapping=user_hash)
            
            # Add to the username index
            self.redis.hset("usernames", user_data['screen_name'], user_id)
        
        # Update rankings
        self.redis.zadd("users:top_followers", {user_id: int(user_data['followers_count'])})
        self.redis.zadd("users:top_posters", {user_id: int(user_data['statuses_count'])})
        
        return user_id
    
    def import_chirp(self, chirp_data):
        """
        Import a chirp into Redis
        
        Args:
            chirp_data (dict): Chirp data
        
        Returns:
            str: ID of the imported chirp
        """
        chirp_id = str(chirp_data['id'])
        user_id = str(chirp_data['user']['id'])
        timestamp = int(chirp_data['timestamp_ms']) / 1000  # Convert to seconds
        
        # Import the user first
        self.import_user(chirp_data['user'])
        
        # Ensure favorite_count and retweet_count have values and are integers
        favorite_count = int(chirp_data.get('favorite_count', 0))
        retweet_count = int(chirp_data.get('retweet_count', 0))
        
        # Create the chirp
        chirp_hash = {
            "text": chirp_data['text'],
            "user_id": user_id,
            "username": chirp_data['user']['screen_name'],
            "created_at": chirp_data['created_at'],
            "lang": chirp_data['lang'],
            "favorite_count": favorite_count,
            "retweet_count": retweet_count
        }
        self.redis.hset(f"chirp:{chirp_id}", mapping=chirp_hash)
        
        # Add to timeline
        self.redis.zadd("chirps:timeline", {chirp_id: timestamp})
        
        # Keep only the 100000 latest chirps in the timeline
        timeline_size = self.redis.zcard("chirps:timeline")
        if timeline_size > 100000:
            # Remove the oldest ones
            to_remove = self.redis.zrange("chirps:timeline", 0, timeline_size - 1001)
            if to_remove:
                self.redis.zrem("chirps:timeline", *to_remove)
        
        return chirp_id
    
    def get_latest_chirps(self, count=5):
        """
        Get the latest chirps
        
        Args:
            count (int): Number of chirps to retrieve
        
        Returns:
            list: List of chirps
        """
        chirp_ids = self.redis.zrevrange("chirps:timeline", 0, count - 1)
        chirps = []
        
        for chirp_id in chirp_ids:
            chirp_data = self.redis.hgetall(f"chirp:{chirp_id}")
            if chirp_data:
                # Ensure favorite_count and retweet_count are integers
                try:
                    chirp_data['favorite_count'] = int(chirp_data.get('favorite_count', 0))
                    chirp_data['retweet_count'] = int(chirp_data.get('retweet_count', 0))
                except (ValueError, TypeError):
                    # If conversion fails, assign default values
                    chirp_data['favorite_count'] = 0
                    chirp_data['retweet_count'] = 0
                
                # Add chirp ID to the data
                chirp_data['chirp_id'] = chirp_id
                chirps.append(chirp_data)
        
        return chirps
    
    def get_top_users_by_followers(self, count=5):
        """
        Get users with the most followers
        
        Args:
            count (int): Number of users to retrieve
        
        Returns:
            list: List of users
        """
        user_ids = self.redis.zrevrange("users:top_followers", 0, count - 1)
        users = []
        
        for user_id in user_ids:
            user_data = self.redis.hgetall(f"users:{user_id}")
            if user_data:
                users.append(user_data)
        
        return users
    
    def get_top_posters(self, count=5):
        """
        Get users who have posted the most chirps
        
        Args:
            count (int): Number of users to retrieve
        
        Returns:
            list: List of users
        """
        user_ids = self.redis.zrevrange("users:top_posters", 0, count - 1)
        users = []
        
        for user_id in user_ids:
            user_data = self.redis.hgetall(f"users:{user_id}")
            if user_data:
                users.append(user_data)
        
        return users
    
    def post_chirp(self, user_id, text):
        """
        Post a new chirp
        
        Args:
            user_id (str): User ID
            text (str): Chirp text
        
        Returns:
            str: ID of the created chirp
        """
        # Check if the user exists
        if not self.redis.exists(f"users:{user_id}"):
            raise ValueError(f"User {user_id} doesn't exist")
        
        # Generate a unique ID
        chirp_id = str(int(time.time() * 1000))
        timestamp = time.time()
        
        # Get user information
        username = self.redis.hget(f"users:{user_id}", "username")
        
        # Create the chirp
        now = datetime.now().strftime("%a %b %d %H:%M:%S +0000 %Y")
        chirp_hash = {
            "text": text,
            "user_id": user_id,
            "username": username,
            "created_at": now,
            "lang": "en",
            "favorite_count": 0,
            "retweet_count": 0
        }
        
        self.redis.hset(f"chirp:{chirp_id}", mapping=chirp_hash)
        
        # Add to timeline
        self.redis.zadd("chirps:timeline", {chirp_id: timestamp})
        
        # Increment the user's chirp counter
        self.redis.hincrby(f"users:{user_id}", "chirp_count", 1)
        
        # Update the poster ranking
        new_count = int(self.redis.hget(f"users:{user_id}", "chirp_count"))
        self.redis.zadd("users:top_posters", {user_id: new_count})
        
        return chirp_id
    
    def like_chirp(self, chirp_id):
        """
        Like a chirp (increment favorite count)
        
        Args:
            chirp_id (str): Chirp ID
            
        Returns:
            int: New favorite count
            
        Raises:
            ValueError: If the chirp doesn't exist
        """
        # Check if the chirp exists
        if not self.redis.exists(f"chirp:{chirp_id}"):
            raise ValueError(f"Chirp {chirp_id} doesn't exist")
            
        # Increment the favorite count
        new_count = self.redis.hincrby(f"chirp:{chirp_id}", "favorite_count", 1)
        return new_count
        
    def rechirp(self, chirp_id):
        """
        Rechirp a chirp (increment retweet count)
        
        Args:
            chirp_id (str): Chirp ID
            
        Returns:
            int: New retweet count
            
        Raises:
            ValueError: If the chirp doesn't exist
        """
        # Check if the chirp exists
        if not self.redis.exists(f"chirp:{chirp_id}"):
            raise ValueError(f"Chirp {chirp_id} doesn't exist")
            
        # Increment the retweet count
        new_count = self.redis.hincrby(f"chirp:{chirp_id}", "retweet_count", 1)
        return new_count
    
    def add_user(self, username, name, profile_image=''):
        """
        Add a new user to the database
        
        Args:
            username (str): Username (screen_name)
            name (str): Full name of the user
            profile_image (str, optional): Profile image URL
        
        Returns:
            str: ID of the created user
        
        Raises:
            ValueError: If the username already exists
        """
        # Check if the username already exists
        if self.redis.hexists("usernames", username):
            raise ValueError(f"The username @{username} already exists")
        
        # Generate a unique new ID (timestamp)
        user_id = str(int(time.time() * 1000))
        
        # Create a new user with default values
        now = datetime.now().strftime("%a %b %d %H:%M:%S +0000 %Y")
        user_hash = {
            "username": username,
            "name": name,
            "follower_count": 0,
            "following_count": 0,
            "chirp_count": 0,
            "created_at": now,
            "profile_image": profile_image
        }
        
        # Save the user in Redis
        self.redis.hset(f"users:{user_id}", mapping=user_hash)
        
        # Add to username index
        self.redis.hset("usernames", username, user_id)
        
        # Add to rankings (with score 0)
        self.redis.zadd("users:top_followers", {user_id: 0})
        self.redis.zadd("users:top_posters", {user_id: 0})
        
        return user_id
    
    def get_top_liked_chirps(self, count=5):
        """
        Get chirps with the most likes
        
        Args:
            count (int): Number of chirps to retrieve
            
        Returns:
            list: List of chirps
        """
        # Get all chirps
        chirp_keys = self.redis.keys("chirp:*")
        
        # Create temporary sorted set for ranking
        temp_key = "temp:top_liked"
        pipe = self.redis.pipeline()
        
        # Delete existing temporary key if it exists
        pipe.delete(temp_key)
        
        # Add each chirp to the temporary sorted set with its favorite count as score
        for key in chirp_keys:
            favorite_count = int(self.redis.hget(key, "favorite_count") or 0)
            pipe.zadd(temp_key, {key.split(":", 1)[1]: favorite_count})
        
        # Execute the pipeline
        pipe.execute()
        
        # Get the top chirps by likes
        top_chirp_ids = self.redis.zrevrange(temp_key, 0, count - 1)
        
        # Clean up temporary key
        self.redis.delete(temp_key)
        
        # Get the full chirp data
        top_chirps = []
        for chirp_id in top_chirp_ids:
            chirp_data = self.redis.hgetall(f"chirp:{chirp_id}")
            if chirp_data:
                # Convert engagement metrics to integers
                chirp_data['favorite_count'] = int(chirp_data.get('favorite_count', 0))
                chirp_data['retweet_count'] = int(chirp_data.get('retweet_count', 0))
                chirp_data['chirp_id'] = chirp_id
                top_chirps.append(chirp_data)
        
        return top_chirps

    def get_top_rechirped_chirps(self, count=5):
        """
        Get chirps with the most retweets
        
        Args:
            count (int): Number of chirps to retrieve
            
        Returns:
            list: List of chirps
        """
        # Get all chirps
        chirp_keys = self.redis.keys("chirp:*")
        
        # Create temporary sorted set for ranking
        temp_key = "temp:top_rechirped"
        pipe = self.redis.pipeline()
        
        # Delete existing temporary key if it exists
        pipe.delete(temp_key)
        
        # Add each chirp to the temporary sorted set with its retweet count as score
        for key in chirp_keys:
            retweet_count = int(self.redis.hget(key, "retweet_count") or 0)
            pipe.zadd(temp_key, {key.split(":", 1)[1]: retweet_count})
        
        # Execute the pipeline
        pipe.execute()
        
        # Get the top chirps by retweets
        top_chirp_ids = self.redis.zrevrange(temp_key, 0, count - 1)
        
        # Clean up temporary key
        self.redis.delete(temp_key)
        
        # Get the full chirp data
        top_chirps = []
        for chirp_id in top_chirp_ids:
            chirp_data = self.redis.hgetall(f"chirp:{chirp_id}")
            if chirp_data:
                # Convert engagement metrics to integers
                chirp_data['favorite_count'] = int(chirp_data.get('favorite_count', 0))
                chirp_data['retweet_count'] = int(chirp_data.get('retweet_count', 0))
                chirp_data['chirp_id'] = chirp_id
                top_chirps.append(chirp_data)
        
        return top_chirps