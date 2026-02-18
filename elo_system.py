"""
ELO Rating System for Ping Pong Matches

This module implements the ELO rating calculation system.
The ELO rating system is a method for calculating the relative skill levels of players.
"""


def calculate_expected_score(player_rating: int, opponent_rating: int) -> float:
    """
    Calculate the expected score for a player.
    
    Args:
        player_rating: Current ELO rating of the player
        opponent_rating: Current ELO rating of the opponent
    
    Returns:
        Expected score (probability of winning) between 0 and 1
    """
    return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))


def calculate_new_rating(current_rating: int, expected_score: float, 
                        actual_score: float, k_factor: int = 32) -> int:
    """
    Calculate the new ELO rating after a match.
    
    Args:
        current_rating: Current ELO rating
        expected_score: Expected score from calculate_expected_score
        actual_score: Actual score (1 for win, 0 for loss, 0.5 for draw)
        k_factor: K-factor determines the maximum rating change (default 32)
    
    Returns:
        New ELO rating (rounded to nearest integer)
    """
    return round(current_rating + k_factor * (actual_score - expected_score))


def process_match(winner_rating: int, defeated_rating: int, k_factor: int = 32) -> tuple[int, int]:
    """
    Process a match and calculate new ELO ratings for both players.
    
    Args:
        winner_rating: Current ELO rating of winner
        defeated_rating: Current ELO rating of defeated player
        k_factor: K-factor for rating adjustment (default 32)
    
    Returns:
        Tuple of (new_rating_winner, new_rating_defeated)
    """
    # Calculate expected scores
    expected_score_winner = calculate_expected_score(winner_rating, defeated_rating)
    expected_score_defeated = calculate_expected_score(defeated_rating, winner_rating)
    
    # Calculate new ratings
    new_rating_winner = calculate_new_rating(winner_rating, expected_score_winner, 1.0, k_factor)
    new_rating_defeated = calculate_new_rating(defeated_rating, expected_score_defeated, 0.0, k_factor)
    
    return new_rating_winner, new_rating_defeated
