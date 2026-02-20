import sqlite3
from typing import Optional, List, Tuple


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

        # Players table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                elo_rating INTEGER DEFAULT 1000,
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
                player_a_elo_before INTEGER NOT NULL,
                player_b_elo_before INTEGER NOT NULL,
                player_a_elo_after INTEGER NOT NULL,
                player_b_elo_after INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                created_by TEXT NOT NULL,
                FOREIGN KEY (player_a_id) REFERENCES players(id),
                FOREIGN KEY (player_b_id) REFERENCES players(id)
            )
        """)
        
        conn.commit()
        conn.close()

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

    def delete_player(self, player_id: int) -> bool:
        """Delete a player."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM players WHERE id = ?", (player_id,))
        conn.commit()
        conn.close()
        return True

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
            SELECT id, name, elo_rating, matches_played, matches_won
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
    def add_match(self, player_winner_id: int, player_defeated_id: int,
                  player_a_elo_before: int, player_b_elo_before: int,
                  player_a_elo_after: int, player_b_elo_after: int,
                  user: dict):
        """Add a new match record."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO matches 
            (player_a_id, player_b_id,
             player_a_elo_before, player_b_elo_before,
             player_a_elo_after, player_b_elo_after, 
             created_by)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (player_winner_id, player_defeated_id,
              player_a_elo_before, player_b_elo_before,
              player_a_elo_after, player_b_elo_after, user['name']))
        
        conn.commit()
        conn.close()

    def delete_match(self, match_id: int):
        """Delete a match record."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            DELETE FROM matches 
            WHERE id = ?
        """, (match_id,))

        conn.commit()
        conn.close()

    def get_recent_matches(self, limit: int = 10) -> List[Tuple]:
        """Get recent matches."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT 
                m.id,
                pa.name, pb.name,
                m.player_a_elo_after, m.player_b_elo_after,
                m.player_a_elo_before, m.player_b_elo_before,
                m.created_at, m.created_by
            FROM matches m
            JOIN players pa ON m.player_a_id = pa.id
            JOIN players pb ON m.player_b_id = pb.id
            ORDER BY m.created_at DESC
            LIMIT ?
        """, (limit,))
        
        result = cursor.fetchall()
        conn.close()

        return result
