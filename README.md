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
chirp-redis-keyvalue-lab/\
├── src/                  # Main source code \
│   ├── models/           # Redis data models\
│   ├── utils/            # Utility functions\
│   └── app/              # Streamlit web app\
├── scripts/              # Utility scripts\
├── data/                 # Generated data\
├── docs/                 # Documentation\
└── tests/                # Unit tests

## Installation

1. Clone this repository:
```bash
git clone https://github.com/your-username/chirp-redis-keyvalue-lab.git
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
source venv/bin/activate  # On Linux/Mac
# or
venv\Scripts\activate  # On Windows

```
4. Install Python dependencies:
```bash
pip install -r requirements.txt
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
6. help - Show help information
7. exit - Exit the application
```

### Reset the database (complementary Feature)
To reset the Redis database:
```bash
python3 scripts/reset_db.py
```

### Running the Web App (Bonus Feature)

Launch the Streamlit web interface:
```bash
streamlit run src/app/streamlit_app.py
```
### Running Tests

To run the unit tests:
```bash
pytest
```
## Data Model

The Redis data model uses various Redis data structures:
- Hash structures for user and chirp data
- Sets for following/follower relationships
- Sorted sets for rankings (by followers, by chirps)
- Lists for recent chirps

For detailed documentation on the data model, see `docs/data_model.md`.

## Authors

- Duc Jeremy

## License

This project is an academic exercise created for the course "Beyond Relational Databases" (205.2) under the MIT License.

## Acknowledgments

- Prof. Dr. Pamela Delgado
- Prof. Dr. René Schumann