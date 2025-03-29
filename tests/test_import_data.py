#!/usr/bin/env python3
"""
Unit tests for the data import functionality
"""

import sys
import os
import json
import pytest
import tempfile
import fakeredis
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from scripts.import_data import import_data
from src.models.redis_model import ChirpRedisModel

class TestDataImport:
    """Test class for the data import functionality"""
    
    @pytest.fixture
    def fake_redis(self):
        """Create a fake Redis client for testing"""
        return fakeredis.FakeStrictRedis(decode_responses=True)
    
    @pytest.fixture
    def sample_tweets(self):
        """Create a sample of tweets for testing import"""
        return [
            {
                "id": 1000001,
                "text": "This is the first test tweet",
                "user": {
                    "id": 101,
                    "name": "User One",
                    "screen_name": "user1",
                    "followers_count": 100,
                    "friends_count": 50,
                    "statuses_count": 200,
                    "created_at": "Mon Apr 01 12:00:00 +0000 2025"
                },
                "created_at": "Mon Apr 01 12:00:00 +0000 2025",
                "timestamp_ms": "1712055000000",
                "favorite_count": 10,
                "retweet_count": 5,
                "lang": "en"
            },
            {
                "id": 1000002,
                "text": "This is the second test tweet",
                "user": {
                    "id": 102,
                    "name": "User Two",
                    "screen_name": "user2",
                    "followers_count": 200,
                    "friends_count": 100,
                    "statuses_count": 300,
                    "created_at": "Mon Apr 01 12:00:00 +0000 2025"
                },
                "created_at": "Mon Apr 01 12:30:00 +0000 2025",
                "timestamp_ms": "1712056800000",
                "favorite_count": 20,
                "retweet_count": 10,
                "lang": "en"
            },
            {
                "id": 1000003,
                "text": "This is the third test tweet",
                "user": {
                    "id": 103,
                    "name": "User Three",
                    "screen_name": "user3",
                    "followers_count": 300,
                    "friends_count": 150,
                    "statuses_count": 400,
                    "created_at": "Mon Apr 01 12:00:00 +0000 2025"
                },
                "created_at": "Mon Apr 01 13:00:00 +0000 2025",
                "timestamp_ms": "1712058600000",
                "favorite_count": 30,
                "retweet_count": 15,
                "lang": "en"
            },
            {
                "id": 1000004,
                "text": "Ceci est un tweet en français",
                "user": {
                    "id": 104,
                    "name": "User Four",
                    "screen_name": "user4",
                    "followers_count": 400,
                    "friends_count": 200,
                    "statuses_count": 500,
                    "created_at": "Mon Apr 01 12:00:00 +0000 2025"
                },
                "created_at": "Mon Apr 01 13:30:00 +0000 2025",
                "timestamp_ms": "1712060400000",
                "favorite_count": 40,
                "retweet_count": 20,
                "lang": "fr"
            }
        ]
    
    def test_import_english_tweets_only(self, fake_redis, sample_tweets, monkeypatch):
        """Test that only English tweets are imported"""
        # Create a temporary file with the sample tweets
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(sample_tweets, f)
            temp_file = f.name
        
        try:
            # Patch the ChirpRedisModel to use fake_redis
            with patch('src.models.redis_model.redis.Redis', return_value=fake_redis):
                # Run the import function
                import_data(temp_file, limit=None, add_engagement=False)
                
                # Check that only the English tweets were imported
                # We should have 3 chirps in the timeline
                assert fake_redis.zcard("chirps:timeline") == 3
                
                # We should have 3 users (excluding ranking keys like users:top_followers)
                user_keys = [key for key in fake_redis.keys("users:*") if not any(key.endswith(suffix) for suffix in ["top_followers", "top_posters"])]
                assert len(user_keys) == 3
                
                # Ensure the French tweet was not imported
                assert not fake_redis.exists("chirp:1000004")
                
                # But all three English tweets should be there
                assert fake_redis.exists("chirp:1000001")
                assert fake_redis.exists("chirp:1000002")
                assert fake_redis.exists("chirp:1000003")
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
    
    def test_import_with_limit(self, fake_redis, sample_tweets, monkeypatch):
        """Test importing with a limit"""
        # Create a temporary file with the sample tweets
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(sample_tweets, f)
            temp_file = f.name
        
        try:
            # Patch the ChirpRedisModel to use fake_redis
            with patch('src.models.redis_model.redis.Redis', return_value=fake_redis):
                # Run the import function with a limit of 2
                import_data(temp_file, limit=2, add_engagement=False)
                
                # We should have only 2 chirps in the timeline
                assert fake_redis.zcard("chirps:timeline") == 2
                
                # The first two English tweets should be there
                assert fake_redis.exists("chirp:1000001")
                assert fake_redis.exists("chirp:1000002")
                
                # But not the third
                assert not fake_redis.exists("chirp:1000003")
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
    
    def test_import_with_engagement(self, fake_redis, sample_tweets, monkeypatch):
        """Test importing with random engagement metrics"""
        # Create a temporary file with the sample tweets
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            json.dump(sample_tweets, f)
            temp_file = f.name
        
        try:
            # Patch the ChirpRedisModel to use fake_redis and random for deterministic testing
            with patch('src.models.redis_model.redis.Redis', return_value=fake_redis):
                with patch('random.randint', side_effect=[100, 50]):  # Fixed values for likes and retweets
                    # Run the import function with add_engagement
                    import_data(temp_file, limit=1, add_engagement=True)
                    
                    # Check that the engagement metrics were updated
                    chirp_data = fake_redis.hgetall("chirp:1000001")
                    assert int(chirp_data["favorite_count"]) == 100  # From the mocked random.randint
                    assert int(chirp_data["retweet_count"]) == 50    # From the mocked random.randint
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)
    
    def test_import_handles_json_decode_error(self, fake_redis, monkeypatch):
        """Test that the import function handles JSON decode errors gracefully"""
        # Create a temporary file with invalid JSON
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write('{"id": 1000001, "invalid JSON')
            temp_file = f.name
        
        try:
            # Patch the ChirpRedisModel to use fake_redis
            with patch('src.models.redis_model.redis.Redis', return_value=fake_redis):
                # This should not raise an exception
                import_data(temp_file)
                
                # We should have 0 chirps in the timeline
                assert fake_redis.zcard("chirps:timeline") == 0
        finally:
            # Clean up the temporary file
            os.unlink(temp_file)