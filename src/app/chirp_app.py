#!/usr/bin/env python3
"""
Chirp Main Application - Implementation of functionalities
"""

import os
import sys
import json
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.redis_model import ChirpRedisModel

class ChirpApp:
    """Main Chirp Application"""
    
    def __init__(self, host='localhost', port=6379, db=0):
        """Initialize Chirp application with a Redis connection"""
        self.model = ChirpRedisModel(host=host, port=port, db=db)
        
    def display_welcome(self):
        """Display a welcome message"""
        print("\n" + "="*80)
        print("                      🐦 CHIRP - Compact Hub for Instant Real-time Posting")
        print("="*80)
        print("\n🎉 Welcome to Chirp, a simplified version of Twitter using Redis.")
        print("Use the commands below to interact with the application.\n")
    
    def display_help(self):
        """Display help and available commands"""
        print("\n📋 Available commands:")
        print("  1. latest - Display the 5 most recent chirps")
        print("  2. topfollowers - Display the 5 users with the most followers")
        print("  3. topposters - Display the 5 users with the most chirps")
        print("  4. post <username> <message> - Post a new chirp")
        print("  5. addUser <username> <name> - Add a new user")
        print("  6. help - Display this help message")
        print("  7. exit - Exit the application")
        print("\n")
    
    def format_chirp(self, chirp):
        """Format a chirp for display"""
        return f"""
  [@{chirp['username']}] - {chirp['created_at']}
  {chirp['text']}
  ♥ {chirp['favorite_count']} | ↺ {chirp['retweet_count']}
        """
    
    def format_user(self, user):
        """Format user information for display"""
        return f"""
  {user['name']} (@{user['username']})
  Followers: {user['follower_count']} | Following: {user['following_count']} | Chirps: {user['chirp_count']}
        """
    
    def display_latest_chirps(self):
        """Display the 5 latest chirps"""
        chirps = self.model.get_latest_chirps(5)
        
        if not chirps:
            print("\n📭 No available chirps.")
            return
        
        print("\n📱 --- 5 latest chirps ---")
        for chirp in chirps:
            print(self.format_chirp(chirp))
    
    def display_top_followers(self):
        """Display the 5 users with the most followers"""
        users = self.model.get_top_users_by_followers(5)
        
        if not users:
            print("\n👻 No available users.")
            return
        
        print("\n🌟 --- Top 5 users (by followers count) ---")
        for i, user in enumerate(users, 1):
            print(f"{i}. {self.format_user(user)}")
    
    def display_top_posters(self):
        """Display the 5 users with the most chirps"""
        users = self.model.get_top_posters(5)
        
        if not users:
            print("\n👻 No available users.")
            return
        
        print("\n✍️ --- Top 5 users (by chirps count) ---")
        for i, user in enumerate(users, 1):
            print(f"{i}. {self.format_user(user)}")
    
    def post_new_chirp(self, username, text):
        """Post a new chirp"""
        # Get the user ID from the username
        user_id = self.model.redis.hget("usernames", username)
        
        if not user_id:
            print(f"\n❌ Error: User @{username} does not exist.")
            return
        
        try:
            chirp_id = self.model.post_chirp(user_id, text)
            print(f"\n✅ Chirp successfully posted! ID: {chirp_id}")
        except Exception as e:
            print(f"\n❌ Error posting chirp: {e}")
    
    def add_new_user(self, username, name):
        """Add a new user"""
        try:
            # Check that the username is valid
            if not username or ' ' in username:
                print(f"\n❌ Error: Username must not contain spaces.")
                return
            
            # Add the user
            user_id = self.model.add_user(username, name)
            print(f"\n👤 User @{username} successfully created! ID: {user_id}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Error creating user: {e}")
    
    def run(self):
        """Run the application in interactive mode"""
        self.display_welcome()
        self.display_help()
        
        while True:
            command = input("\nChirp> ").strip()
            
            if command.lower() == "exit":
                print("👋 Goodbye!")
                break
            
            elif command.lower() == "help":
                self.display_help()
            
            elif command.lower() == "latest":
                self.display_latest_chirps()
            
            elif command.lower() == "topfollowers":
                self.display_top_followers()
            
            elif command.lower() == "topposters":
                self.display_top_posters()
            
            elif command.lower().startswith("post "):
                # Format: post username message
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    print("⚠️ Incorrect format. Use: post <username> <message>")
                else:
                    _, username, text = parts
                    self.post_new_chirp(username, text)
            
            elif command.lower().startswith("adduser "):
                # Format: addUser username name
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    print("⚠️ Incorrect format. Use: addUser <username> <name>")
                else:
                    _, username, name = parts
                    self.add_new_user(username, name)
            
            else:
                print(f"❓ Unknown command: {command}")
                self.display_help()

if __name__ == "__main__":
    # Create and run the application
    app = ChirpApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n🛑 Application interrupted. Goodbye! 👋")
    except Exception as e:
        print(f"\n⚠️ Unexpected error: {e}")