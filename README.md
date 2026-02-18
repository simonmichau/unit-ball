# unit-ball
Elo Tracker for Ping Pong

A Streamlit web application for tracking ping pong match results using an ELO rating system with user authentication.

## Features

- 🔐 **User Authentication**: Secure login and registration system
- 🏓 **Match Recording**: Enter match results with player scores
- 📊 **ELO Rating System**: Automatic calculation of player rankings using the ELO algorithm
- 🏆 **Leaderboard**: View player rankings with ELO ratings, matches played, and win rates
- 📜 **Match History**: Track recent match results

## Installation

1. Clone the repository:
```bash
git clone https://github.com/simonmichau/unit-ball.git
cd unit-ball
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the application:
```bash
streamlit run app.py
```

2. Open your browser and navigate to the URL shown (typically `http://localhost:8501`)

3. Register a new user account or login with existing credentials

4. Add players using the sidebar

5. Record matches and watch the leaderboard update with ELO ratings!

## How It Works

### ELO Rating System

The application uses the ELO rating system to calculate relative skill levels:
- New players start with a rating of 1500
- Winners gain points, losers lose points
- The amount of change depends on the rating difference between players
- Beating a higher-rated player gives more points than beating a lower-rated player

### Database

The application uses SQLite to store:
- User accounts (with hashed passwords)
- Player profiles and statistics
- Match history with ELO changes

## Project Structure

```
unit-ball/
├── app.py              # Main Streamlit application
├── database.py         # Database management and queries
├── elo_system.py       # ELO rating calculations
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Security

- Passwords are hashed using bcrypt before storage
- Database is stored locally (pingpong.db)
- Session-based authentication using Streamlit's session state
