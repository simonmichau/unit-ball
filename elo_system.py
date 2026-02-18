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


def process_match(player_a_rating: int, player_b_rating: int,
                 player_a_points: int, player_b_points: int,
                 k_factor: int = 32) -> tuple[int, int]:
    """
    Process a match and calculate new ELO ratings for both players.
    
    Args:
        player_a_rating: Current ELO rating of player A
        player_b_rating: Current ELO rating of player B
        player_a_points: Points scored by player A
        player_b_points: Points scored by player B
        k_factor: K-factor for rating adjustment (default 32)
    
    Returns:
        Tuple of (new_rating_a, new_rating_b)
    """
    # Calculate expected scores
    expected_a = calculate_expected_score(player_a_rating, player_b_rating)
    expected_b = calculate_expected_score(player_b_rating, player_a_rating)
    
    # Determine actual scores based on match result
    if player_a_points > player_b_points:
        actual_a = 1.0
        actual_b = 0.0
    elif player_b_points > player_a_points:
        actual_a = 0.0
        actual_b = 1.0
    else:
        actual_a = 0.5
        actual_b = 0.5
    
    # Calculate new ratings
    new_rating_a = calculate_new_rating(player_a_rating, expected_a, actual_a, k_factor)
    new_rating_b = calculate_new_rating(player_b_rating, expected_b, actual_b, k_factor)
    
    return new_rating_a, new_rating_b
