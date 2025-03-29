#!/usr/bin/env python3
"""
Unit tests for the Streamlit app
Note: Testing Streamlit apps is challenging since they rely on the Streamlit UI.
These tests focus on the functionality rather than the UI elements.
"""

import sys
import os
import pytest
import fakeredis
from unittest.mock import patch, MagicMock

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.models.redis_model import ChirpRedisModel

# Create a mock for streamlit since we can't actually render the UI in tests
class MockStreamlit:
    """Mock class for streamlit"""
    def __init__(self):
        self.sidebar = MagicMock()
        self.session_state = {}
        self.containers = []
        self.columns = []
        self.tabs = []
        self.title_text = None
        self.header_text = None
        self.subheader_text = None
        self.markdown_text = []
        self.info_messages = []
        self.success_messages = []
        self.error_messages = []
        self.form_submit_results = []
        self.button_clicks = []
        self.selectbox_selections = []
        self.text_input_values = []
        self.text_area_values = []
        self.checkbox_values = []
        self.metric_values = []
    
    def title(self, text):
        self.title_text = text
    
    def header(self, text):
        self.header_text = text
    
    def subheader(self, text):
        self.subheader_text = text
    
    def markdown(self, text):
        self.markdown_text.append(text)
    
    def info(self, text):
        self.info_messages.append(text)
    
    def success(self, text):
        self.success_messages.append(text)
    
    def error(self, text):
        self.error_messages.append(text)
    
    def container(self):
        container = MagicMock()
        self.containers.append(container)
        return container
    
    def columns(self, widths):
        columns = [MagicMock() for _ in widths]
        self.columns.append(columns)
        return columns
    
    def tabs(self, names):
        tabs = [MagicMock() for _ in names]
        self.tabs.append(tabs)
        return tabs
    
    def form(self, key):
        form = MagicMock()
        # Form will return success for form_submit_button
        form.form_submit_button.return_value = self.form_submit_results.pop(0) if self.form_submit_results else False
        return form
    
    def button(self, text, key=None):
        return self.button_clicks.pop(0) if self.button_clicks else False
    
    def selectbox(self, label, options, key=None):
        return self.selectbox_selections.pop(0) if self.selectbox_selections else (options[0] if options else None)
    
    def text_input(self, label, key=None):
        return self.text_input_values.pop(0) if self.text_input_values else ""
    
    def text_area(self, label, max_chars=None, key=None):
        return self.text_area_values.pop(0) if self.text_area_values else ""
    
    def checkbox(self, label, key=None):
        return self.checkbox_values.pop(0) if self.checkbox_values else False
    
    def metric(self, label, value):
        self.metric_values.append((label, value))
    
    def rerun(self):
        pass
    
    def image(self, image_path, width=None):
        pass
    
    def text(self, text):
        pass

    # Mock cache decorator to make it do nothing
    def cache_resource(self, func):
        return func
    
    # Mock set_page_config
    def set_page_config(self, page_title=None, page_icon=None, layout=None):
        pass

class TestStreamlitApp:
    """Test class for the Streamlit app"""
    
    @pytest.fixture
    def mock_st(self):
        """Create a mock streamlit object"""
        return MockStreamlit()
    
    @pytest.fixture
    def fake_redis(self):
        """Create a fake Redis client for testing"""
        return fakeredis.FakeStrictRedis(decode_responses=True)
    
    @pytest.fixture
    def model(self, fake_redis):
        """Create a ChirpRedisModel with a fake Redis client"""
        # Monkey patch the Redis client in the model
        ChirpRedisModel.redis = fake_redis
        model = ChirpRedisModel()
        model.reset_db()  # Start with a clean database
        return model
    
    @pytest.fixture
    def sample_data(self, model):
        """Create some sample data for testing"""
        # Add sample users
        for i in range(1, 6):
            user_id = str(1000 + i)
            model.redis.hset(f"users:{user_id}", mapping={
                "username": f"user{i}",
                "name": f"User {i}",
                "follower_count": i * 100,
                "following_count": i * 50,
                "chirp_count": i * 10,
                "created_at": "Mon Apr 01 12:00:00 +0000 2025"
            })
            model.redis.hset("usernames", f"user{i}", user_id)
            model.redis.zadd("users:top_followers", {user_id: i * 100})
            model.redis.zadd("users:top_posters", {user_id: i * 10})
        
        # Add sample chirps
        for i in range(1, 11):
            chirp_id = str(2000 + i)
            user_id = str(1000 + (i % 5) + 1)  # Cycle through the 5 users
            model.redis.hset(f"chirp:{chirp_id}", mapping={
                "text": f"This is test chirp {i}",
                "user_id": user_id,
                "username": f"user{(i % 5) + 1}",
                "created_at": f"Mon Apr 01 {12+i}:00:00 +0000 2025",
                "lang": "en",
                "favorite_count": i * 5,
                "retweet_count": i * 2
            })
            model.redis.zadd("chirps:timeline", {chirp_id: 1712055000000 + (i * 1000)})
    
    def test_model_get_latest_chirps(self, model, sample_data):
        """Test that the model can get the latest chirps"""
        # Get the latest chirps using the model
        latest_chirps = model.get_latest_chirps(5)
        
        # Check that we got 5 chirps
        assert len(latest_chirps) == 5
        
        # Check that they are sorted by timestamp (newest first)
        chirp_ids = [int(chirp['chirp_id']) for chirp in latest_chirps]
        assert chirp_ids == sorted(chirp_ids, reverse=True)
    
    def test_model_post_chirp(self, model, sample_data):
        """Test that the model can post a new chirp"""
        # Get a user ID to post as
        user_id = model.redis.hget("usernames", "user1")
        
        # Count chirps before
        chirp_count_before = model.redis.zcard("chirps:timeline")
        
        # Post a new chirp
        chirp_id = model.post_chirp(user_id, "This is a test chirp")
        
        # Count chirps after
        chirp_count_after = model.redis.zcard("chirps:timeline")
        
        # Check that a new chirp was added
        assert chirp_count_after == chirp_count_before + 1
        
        # Check the chirp content
        chirp_data = model.redis.hgetall(f"chirp:{chirp_id}")
        assert chirp_data["text"] == "This is a test chirp"
    
    def test_model_like_chirp(self, model, sample_data):
        """Test that the model can like a chirp"""
        # Get a chirp ID to like
        chirp_id = model.redis.zrevrange("chirps:timeline", 0, 0)[0]
        
        # Get initial favorite count
        initial_count = int(model.redis.hget(f"chirp:{chirp_id}", "favorite_count"))
        
        # Like the chirp
        new_count = model.like_chirp(chirp_id)
        
        # Check that the favorite count was incremented
        assert new_count == initial_count + 1
    
    def test_model_add_user(self, model):
        """Test that the model can add a new user"""
        # Add a new user
        user_id = model.add_user("newuser", "New Test User")
        
        # Check user data
        user_data = model.redis.hgetall(f"users:{user_id}")
        assert user_data["username"] == "newuser"
        assert user_data["name"] == "New Test User"