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
        print("  2. topFollowers - Display the 5 users with the most followers")
        print("  3. topPosters - Display the 5 users with the most chirps")
        print("  4. topLiked - Display the 5 most liked chirps")
        print("  5. topRechirped - Display the 5 most rechirped chirps")
        print("  6. post <username> <message> - Post a new chirp")
        print("  7. addUser <username> <name> - Add a new user")
        print("  8. like <chirp_id> - Like a chirp")
        print("  9. rechirp <chirp_id> - Rechirp a chirp")
        print("  10. help - Display this help message")
        print("  11. exit - Exit the application")
        print("\n")
    
    def format_chirp(self, chirp):
        """Format a chirp for display"""
        chirp_id = chirp.get('chirp_id', 'unknown')
        return f"""
  [@{chirp['username']}] - {chirp['created_at']}
  {chirp['text']}
  ♥ {chirp['favorite_count']} | ↺ {chirp['retweet_count']} | ID: {chirp_id}
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
        # Get chirp IDs from timeline
        chirp_ids = self.model.redis.zrevrange("chirps:timeline", 0, 4)
        
        for i, chirp in enumerate(chirps):
            if i < len(chirp_ids):
                chirp['chirp_id'] = chirp_ids[i]
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
    
    def like_chirp(self, chirp_id):
        """Like a chirp"""
        try:
            new_count = self.model.like_chirp(chirp_id)
            print(f"\n❤️ Chirp liked! New favorite count: {new_count}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Error liking chirp: {e}")
    
    def rechirp(self, chirp_id):
        """Rechirp a chirp"""
        try:
            new_count = self.model.rechirp(chirp_id)
            print(f"\n🔄 Chirp rechirped! New retweet count: {new_count}")
        except ValueError as e:
            print(f"\n❌ Error: {e}")
        except Exception as e:
            print(f"\n❌ Error rechirping: {e}")
    
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
    
    def display_top_liked(self):
        """Display the 5 chirps with the most likes"""
        chirps = self.model.get_top_liked_chirps(5)
        
        if not chirps:
            print("\n📭 No available chirps.")
            return
        
        print("\n❤️ --- Top 5 most liked chirps ---")
        for i, chirp in enumerate(chirps, 1):
            print(f"{i}. {self.format_chirp(chirp)}")

    def display_top_rechirped(self):
        """Display the 5 chirps with the most rechirps"""
        chirps = self.model.get_top_rechirped_chirps(5)
        
        if not chirps:
            print("\n📭 No available chirps.")
            return
        
        print("\n🔄 --- Top 5 most rechirped chirps ---")
        for i, chirp in enumerate(chirps, 1):
            print(f"{i}. {self.format_chirp(chirp)}")
    
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
            
            elif command.lower() == "topfollowers" or command.lower() == "topFollowers":
                self.display_top_followers()

            elif command.lower() == "topposters" or command.lower() == "topPosters":
                self.display_top_posters()

            elif command.lower() == "topliked" or command.lower() == "topLiked":
                self.display_top_liked()

            elif command.lower() == "toprechirped" or command.lower() == "topRechirped":
                self.display_top_rechirped()
            
            elif command.lower().startswith("post "):
                # Format: post username message
                parts = command.split(" ", 2)
                if len(parts) < 3:
                    print("⚠️ Incorrect format. Use: post <username> <message>")
                else:
                    _, username, text = parts
                    self.post_new_chirp(username, text)
            
            elif command.lower().startswith("like "):
                # Format: like chirp_id
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("⚠️ Incorrect format. Use: like <chirp_id>")
                else:
                    _, chirp_id = parts
                    self.like_chirp(chirp_id)
            
            elif command.lower().startswith("rechirp "):
                # Format: rechirp chirp_id
                parts = command.split(" ", 1)
                if len(parts) < 2:
                    print("⚠️ Incorrect format. Use: rechirp <chirp_id>")
                else:
                    _, chirp_id = parts
                    self.rechirp(chirp_id)
            
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