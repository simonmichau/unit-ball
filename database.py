import sqlite3
import bcrypt
from typing import Optional, List, Tuple
from datetime import datetime


class Database:
    def __init__(self, db_path: str = "pingpong.db"):
        self.db_path = db_path
        self.init_db()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_db(self):
        """Initialize the database with required tables."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                elo_rating INTEGER DEFAULT 1500,
                matches_played INTEGER DEFAULT 0,
                matches_won INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_a_id INTEGER NOT NULL,
                player_b_id INTEGER NOT NULL,
                player_a_points INTEGER NOT NULL,
                player_b_points INTEGER NOT NULL,
                player_a_elo_before INTEGER NOT NULL,
                player_b_elo_before INTEGER NOT NULL,
                player_a_elo_after INTEGER NOT NULL,
                player_b_elo_after INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by INTEGER,
                FOREIGN KEY (player_a_id) REFERENCES players(id),
                FOREIGN KEY (player_b_id) REFERENCES players(id),
                FOREIGN KEY (created_by) REFERENCES users(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    # User authentication methods
    def create_user(self, username: str, password: str) -> bool:
        """Create a new user with hashed password."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Hash the password and decode to string for storage
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def verify_user(self, username: str, password: str) -> bool:
        """Verify user credentials."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,)
        )
        result = cursor.fetchone()
        conn.close()
        
        if result:
            stored_hash = result[0]
            # Convert stored hash to bytes if it's a string
            if isinstance(stored_hash, str):
                stored_hash = stored_hash.encode('utf-8')
            return bcrypt.checkpw(password.encode('utf-8'), stored_hash)
        return False
    
    def get_user_id(self, username: str) -> Optional[int]:
        """Get user ID by username."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    # Player methods
    def create_player(self, name: str) -> bool:
        """Create a new player."""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO players (name) VALUES (?)",
                (name,)
            )
            conn.commit()
            conn.close()
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_player_id(self, name: str) -> Optional[int]:
        """Get player ID by name."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM players WHERE name = ?", (name,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else None
    
    def get_all_players(self) -> List[Tuple]:
        """Get all players ordered by ELO rating."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT name, elo_rating, matches_played, matches_won
            FROM players
            ORDER BY elo_rating DESC
        """)
        result = cursor.fetchall()
        conn.close()
        
        return result
    
    def get_player_elo(self, player_id: int) -> int:
        """Get player's current ELO rating."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT elo_rating FROM players WHERE id = ?", (player_id,))
        result = cursor.fetchone()
        conn.close()
        
        return result[0] if result else 1500
    
    def update_player_stats(self, player_id: int, new_elo: int, won: bool):
        """Update player's ELO and statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if won:
            cursor.execute("""
                UPDATE players 
                SET elo_rating = ?, 
                    matches_played = matches_played + 1,
                    matches_won = matches_won + 1
                WHERE id = ?
            """, (new_elo, player_id))
        else:
            cursor.execute("""
                UPDATE players 
                SET elo_rating = ?, 
                    matches_played = matches_played + 1
                WHERE id = ?
            """, (new_elo, player_id))
        
        conn.commit()
        conn.close()
    
    # Match methods
    def add_match(self, player_a_id: int, player_b_id: int, 
                  player_a_points: int, player_b_points: int,
                  player_a_elo_before: int, player_b_elo_before: int,
                  player_a_elo_after: int, player_b_elo_after: int,
                  user_id: int):
        """Add a new match record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO matches 
            (player_a_id, player_b_id, player_a_points, player_b_points,
             player_a_elo_before, player_b_elo_before,
             player_a_elo_after, player_b_elo_after, created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (player_a_id, player_b_id, player_a_points, player_b_points,
              player_a_elo_before, player_b_elo_before,
              player_a_elo_after, player_b_elo_after, user_id))
        
        conn.commit()
        conn.close()
    
    def get_recent_matches(self, limit: int = 10) -> List[Tuple]:
        """Get recent matches."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                pa.name, pb.name,
                m.player_a_points, m.player_b_points,
                m.player_a_elo_after, m.player_b_elo_after,
                m.created_at
            FROM matches m
            JOIN players pa ON m.player_a_id = pa.id
            JOIN players pb ON m.player_b_id = pb.id
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (limit,))
        
        result = cursor.fetchall()
        conn.close()
        
        return result
