"""This module provides functions for generating Sudoku boards with configurable difficulty."""

from typing import List
import numpy as np
from dokusan import generators, stats
from solver import solve

# Difficulty levels (higher number = harder puzzle)
DIFFICULTY_EASY = 50
DIFFICULTY_MEDIUM = 100
DIFFICULTY_HARD = 150
DIFFICULTY_EXPERT = 200

def generate_board(difficulty: int = DIFFICULTY_MEDIUM) -> np.ndarray:
    """
    Generate a Sudoku board with the specified difficulty level.
    
    Args:
        difficulty: The difficulty level of the puzzle (higher = harder).
                   Default is DIFFICULTY_MEDIUM (100).
    
    Returns:
        A 9x9 numpy array representing the Sudoku board, where empty cells are 0.
    
    Raises:
        ValueError: If difficulty is less than 0.
    """
    if difficulty < 0:
        raise ValueError("Difficulty must be a non-negative number")
    
    while True:
        board = generators.random_sudoku(avg_rank=difficulty)
        board_str = str(board)
        board_list = [int(digit) for digit in board_str]
        board_array = np.array(board_list).reshape(9, 9)
        
        # Make a copy to verify solvability
        board_copy = board_array.copy()
        if solve(board_copy):
            # Board is solvable, return it
            return board_array
        
        # If not solvable, continue loop to generate a new board