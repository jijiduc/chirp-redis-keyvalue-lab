#!/usr/bin/env python3
"""
Streamlit Web App for Chirp - A Compact Hub for Instant Real-time Posting
"""
import os
import sys
import time
import streamlit as st
from datetime import datetime

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.redis_model import ChirpRedisModel

# Initialize the Redis model
@st.cache_resource
def get_model():
    """Get or create a Redis model instance"""
    return ChirpRedisModel(host='localhost', port=6379, db=0)

# Set up the page
st.set_page_config(
    page_title="Chirp - Compact Hub for Instant Real-time Posting",
    page_icon="🐦",
    layout="wide"
)

# Initialize the model
model = get_model()

# App header and description
st.title("🐦 Chirp")
st.subheader("Compact Hub for Instant Real-time Posting")
st.markdown("---")

# Create sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Home", "Post a Chirp", "Top Users", "About"]
)

# Function to format a chirp as a card
def display_chirp(chirp):
    chirp_id = chirp.get('chirp_id', 'unknown')
    
    # Create a container for the chirp
    with st.container():
        col1, col2 = st.columns([1, 6])
        
        with col1:
            # Display user avatar placeholder
            st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=" + chirp['username'], width=50)
        
        with col2:
            # Display chirp content
            st.markdown(f"**@{chirp['username']}** - {chirp['created_at']}")
            st.markdown(chirp['text'])
            
            # Create a row for chirp actions
            col_like, col_rechirp, col_id = st.columns([1, 1, 5])
            
            with col_like:
                # Create a like button
                if st.button(f"♥ {chirp['favorite_count']}", key=f"like_{chirp_id}"):
                    try:
                        new_count = model.like_chirp(chirp_id)
                        st.success(f"Liked! New count: {new_count}")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col_rechirp:
                # Create a rechirp button
                if st.button(f"↺ {chirp['retweet_count']}", key=f"rechirp_{chirp_id}"):
                    try:
                        new_count = model.rechirp(chirp_id)
                        st.success(f"Rechirped! New count: {new_count}")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
            
            with col_id:
                st.text(f"ID: {chirp_id}")
        
        # Divider between chirps
        st.markdown("---")

# Home page
if page == "Home":
    # Add tabs for different views
    tab1, tab2, tab3 = st.tabs(["Latest Chirps", "Most Liked", "Most Rechirped"])
    
    with tab1:
        st.header("Latest Chirps")
        chirps = model.get_latest_chirps(5)
        
        if not chirps:
            st.info("No chirps available. Be the first to post!")
        else:
            for chirp in chirps:
                display_chirp(chirp)
    
    with tab2:
        st.header("Most Liked Chirps")
        top_liked = model.get_top_liked_chirps(5)
        
        if not top_liked:
            st.info("No chirps available.")
        else:
            for chirp in top_liked:
                display_chirp(chirp)
    
    with tab3:
        st.header("Most Rechirped Chirps")
        top_rechirped = model.get_top_rechirped_chirps(5)
        
        if not top_rechirped:
            st.info("No chirps available.")
        else:
            for chirp in top_rechirped:
                display_chirp(chirp)

# Post a Chirp page
elif page == "Post a Chirp":
    st.header("Post a New Chirp")
    
    # Get all usernames for the dropdown
    all_usernames = list(model.redis.hgetall("usernames").keys())
    
    if not all_usernames:
        st.warning("No users found. Please add a user first.")
        
        # Form to add a new user
        st.subheader("Add a New User")
        with st.form("add_user_form"):
            new_username = st.text_input("Username (without @)")
            new_name = st.text_input("Full Name")
            submit_user = st.form_submit_button("Add User")
            
            if submit_user and new_username and new_name:
                try:
                    user_id = model.add_user(new_username, new_name)
                    st.success(f"User @{new_username} created with ID: {user_id}")
                    all_usernames.append(new_username)
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")
    else:
        # Form to post a new chirp
        with st.form("post_chirp_form"):
            username = st.selectbox("Post as", all_usernames)
            chirp_text = st.text_area("What's happening?", max_chars=280)
            submit_chirp = st.form_submit_button("Chirp")
            
            if submit_chirp and chirp_text:
                user_id = model.redis.hget("usernames", username)
                try:
                    chirp_id = model.post_chirp(user_id, chirp_text)
                    st.success(f"Chirp posted with ID: {chirp_id}")
                    # Sleep a bit to show the success message
                    time.sleep(1)
                    # Refresh the page
                    st.rerun()
                except Exception as e:
                    st.error(f"Error posting chirp: {e}")
        
        # Add user form below the post form
        st.subheader("Add a New User")
        with st.form("add_user_form"):
            new_username = st.text_input("Username (without @)")
            new_name = st.text_input("Full Name")
            submit_user = st.form_submit_button("Add User")
            
            if submit_user and new_username and new_name:
                try:
                    user_id = model.add_user(new_username, new_name)
                    st.success(f"User @{new_username} created with ID: {user_id}")
                    all_usernames.append(new_username)
                    st.rerun()
                except ValueError as e:
                    st.error(f"Error: {e}")

# Top Users page
elif page == "Top Users":
    tab1, tab2 = st.tabs(["Most Followers", "Most Chirps"])
    
    with tab1:
        st.header("Users With Most Followers")
        top_followers = model.get_top_users_by_followers(5)
        
        if not top_followers:
            st.info("No users available.")
        else:
            for i, user in enumerate(top_followers, 1):
                with st.container():
                    col1, col2 = st.columns([1, 6])
                    
                    with col1:
                        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=" + user['username'], width=50)
                    
                    with col2:
                        st.markdown(f"**{i}. {user['name']} (@{user['username']})**")
                        st.text(f"Followers: {user['follower_count']} | Following: {user['following_count']} | Chirps: {user['chirp_count']}")
                    
                    st.markdown("---")
    
    with tab2:
        st.header("Users With Most Chirps")
        top_posters = model.get_top_posters(5)
        
        if not top_posters:
            st.info("No users available.")
        else:
            for i, user in enumerate(top_posters, 1):
                with st.container():
                    col1, col2 = st.columns([1, 6])
                    
                    with col1:
                        st.image("https://api.dicebear.com/7.x/avataaars/svg?seed=" + user['username'], width=50)
                    
                    with col2:
                        st.markdown(f"**{i}. {user['name']} (@{user['username']})**")
                        st.text(f"Followers: {user['follower_count']} | Following: {user['following_count']} | Chirps: {user['chirp_count']}")
                    
                    st.markdown("---")

# About page
elif page == "About":
    st.header("About Chirp")
    st.markdown("""
    **Chirp (Compact Hub for Instant Real-time Posting)** is a lightweight Twitter clone
    built as a laboratory project for the "205.2 Beyond Relational Databases" course.
    
    ## Features
    
    - View latest chirps
    - Like and rechirp posts
    - Post new chirps
    - View top users by followers and post count
    - Simple and intuitive interface
    
    ## Technology
    
    Chirp uses Redis as a key-value database to store and retrieve data in real-time.
    The web interface is built with Streamlit, a Python framework for creating interactive
    web applications.
    
    ## Author
    
    - Duc Jeremy
    """)

# Add Redis database status in the sidebar
st.sidebar.markdown("---")
st.sidebar.subheader("Database Status")
chirp_count = model.redis.zcard("chirps:timeline")
user_count = len(model.redis.keys("users:*"))

st.sidebar.metric("Total Chirps", chirp_count)
st.sidebar.metric("Total Users", user_count)

# Add a database reset button in the sidebar
st.sidebar.markdown("---")
if st.sidebar.button("Reset Database"):
    confirmation = st.sidebar.checkbox("Are you sure? This will delete all data.")
    if confirmation:
        model.reset_db()
        st.sidebar.success("Database reset successfully!")
        time.sleep(1)
        st.rerun()

if __name__ == "__main__":
    print("Streamlit Chirp App is running")