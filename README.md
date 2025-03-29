# Chirp - Redis Key-Value Database Lab

A lightweight Twitter clone implemented using Redis key-value database. This project is a laboratory part of the "205.2 Beyond Relational Databases" course lectured at the "Haute Ecole d'Ingénieurie" de Sion.

## Overview

Chirp (Compact Hub for Instant Real-time Posting) is a simplified Twitter-like application that demonstrates the use of Redis as a key-value store for social media data. The application supports:

- User profiles with follower/following counts
- Text-only posts ("chirps")
- Top users tracking
- Latest chirps feed

## Requirements

- Redis server (6.0+)
- Python 3.8+
- Additional Python packages (see requirements.txt)

## Project Structure
```bash
chirp-redis-keyvalue-lab/
├── src/                     # Main source code 
│   ├── app/                 # Application code
│       ├── __init__.py
│       ├── chirp_app.py     # Command-line application
│       └── streamlit_app.py # Web application (to be implemented)
│   └── models/              # Redis data models
│       ├── __init__.py      
│       └── redis_model.py   # Core Redis data model implementation
├── scripts/                 # Utility scripts
│   ├── import_data.py       # Data import script
│   ├── process_jsonl.py     # Data processing script
│   ├── reset_db.py          # Database reset script
│   ├── run_app.py           # Application launcher
│   └── fix_engagement.py    # Script to add engagement metrics
├── data/                    # Generated data
    └── processed/           # Processed data directory
└── tests/
    ├── __init__.py            # (peut être un fichier vide)
    ├── conftest.py            # (celui que j'ai créé)
    ├── test_redis_model.py    # (celui que j'ai créé)
    ├── test_import_data.py    # (celui que j'ai créé)
    └── test_streamlit_app.py  # (celui que j'ai créé)
```

## Installation

1. Clone this repository:
```bash
git clone https://github.com/jijiduc/chirp-redis-keyvalue-lab
cd chirp-redis-keyvalue-lab
```
2. Install Redis server (if not already installed):
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install redis-server

# Start Redis
sudo systemctl start redis-server
```
3. Set up a Python virtual environment and install dependencies:
```bash
python -m venv venv
source venv/bin/activate  # On Linux

```
4. Install Python dependencies:
```bash
pip install -r requirements.txt

# for dev testing
pip install -r requirements-dev.txt
pip install pytest-cov
```
## Usage

### Data Processing and Importing

#### Step 1: Process Twitter Data
Process and extract English tweets from the raw .bz2 files:
```bash
python3 scripts/process_jsonl.py ./data/twitter_data
```
This will create a sample of English tweets in ./data/processed/english_tweets.json.

#### Step 2: Import Data to Redis
After processing the Twitter data, import it into Redis:
```bash
# Import data from the processed JSON file
python3 scripts/import_data.py ./data/processed/english_tweets.json

# Optional flags:
# --limit N     : Import only N tweets (useful for testing)
# --reset       : Reset the database before importing
# --host HOST   : Redis host (default: localhost)
# --port PORT   : Redis port (default: 6379)
# --db DB       : Redis database number (default: 0)
# --add-engagement    : Add random engagement metrics to tweets
```
#### Step 3: Run the Chirp Application
After importing data, you can run the application:
```bash
python3 scripts/run_app.py
```
Available commands in the application:
```bash
1. latest - Show the 5 most recent chirps
2. topfollowers - Display top 5 users with the most followers
3. topposters - Display top 5 users with the most chirps
4. post <username> <message> - Post a new chirp
5. addUser <username> <name> - Add a new user
6. like <chirp_id> - Like a chirp
7. rechirp <chirp_id> - Rechirp a chirp
8. help - Show help information
9. exit - Exit the application
```

### Reset the database
To reset the Redis database:
```bash
python3 scripts/reset_db.py
```

### Running the Web App

Launch the Streamlit web interface:
```bash
streamlit run src/app/streamlit_app.py
```
### Running Tests

To run the unit tests:
```bash
# without a rapport
python3 scripts/run_tests.py

# with a rapport
python -m pytest tests/ -v --cov=src --cov=scripts --cov-report=term --cov-report=html
```
## Data Model
The Redis data model uses various Redis data structures:

- Hash structures for user and chirp data
- Sets for following/follower relationships
- Sorted sets for rankings (by followers, by chirps)
- Lists for recent chirps

Key features of the data model:

- ```users:{user_id}``` - Hash containing user profile data
- ```chirp:{chirp_id}``` - Hash containing chirp data
- ```chirps:timeline``` - Sorted set of chirps by timestamp
- ```users:top_followers``` - Sorted set of users by follower count
- ```users:top_posters``` - Sorted set of users by chirp count
- ```usernames``` - Hash mapping usernames to user IDs

## Engagement Metrics
### Understanding the Data
When importing Twitter data, you may notice that many chirps show zero likes and retweets:
```bash
Copier📱 --- 5 latest chirps ---
  [@username] - Fri Jan 01 06:59:59 +0000 2021
  This is an example chirp
  ♥ 0 | ↺ 0
```

This occurs because:

1. Raw Twitter data often has zero engagement when collected soon after posting
2. The default import process preserves these original values

### Adding Realistic Engagement
To make the application more realistic, you can add randomized engagement metrics to existing chirps using the provided script:
```bash
# Add random likes and retweets to all existing chirps
python scripts/fix_engagement.py

# Additional options:
# --min-likes N      : Minimum number of likes (default: 5)
# --max-likes N      : Maximum number of likes (default: 500)
# --max-retweets N   : Maximum number of retweets (default: 200)
# --host HOST        : Redis host (default: localhost)
# --port PORT        : Redis port (default: 6379)
# --db DB            : Redis database number (default: 0)
```

### Importing Data with Engagement
When importing new data, use the ```--add-engagement``` flag to automatically add random engagement metrics:
```bash
# Import with randomized engagement metrics
python scripts/import_data.py ./data/processed/english_tweets.json --add-engagement
```
### Interacting with Chirps
You can also interact with chirps directly in the application:
```bash
# View the latest chirps to see their IDs
latest

# Like a chirp
like <chirp_id>

# Rechirp (retweet) a chirp
rechirp <chirp_id>
```
These interactions will update the engagement metrics in real-time, providing a more realistic social media experience.

## Authors

- Duc Jeremy

## License

This project is an academic exercise created for the course "Beyond Relational Databases" (205.2) under the MIT License.

## Acknowledgments

- Prof. Dr. Pamela Delgado
- Prof. Dr. René Schumann