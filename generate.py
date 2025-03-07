"""This module provides functions for generating Sudoku boards with configurable difficulty."""

from typing import List
import random
from sudoku import Sudoku

# Difficulty levels (0.0 = easiest, 1.0 = hardest)
DIFFICULTY_EASY = 0.3
DIFFICULTY_MEDIUM = 0.5
DIFFICULTY_HARD = 0.7
DIFFICULTY_EXPERT = 0.9

def generate_board(difficulty: float = DIFFICULTY_MEDIUM) -> List[List[int]]:
    """
    Generate a valid and solvable Sudoku board with the specified difficulty level.
    
    Args:
        difficulty: The difficulty level of the puzzle (0.0-1.0, where 1.0 is hardest).
                   Default is DIFFICULTY_MEDIUM (0.5).
    
    Returns:
        A 9x9 list of lists representing the Sudoku board, where empty cells are 0.
        
    Raises:
        ValueError: If difficulty is not between 0.0 and 1.0.
    """
    if not 0.0 <= difficulty <= 1.0:
        raise ValueError("Difficulty must be between 0.0 and 1.0")
    
    # Add some randomness to the seed to ensure different boards
    random.seed()
    seed = random.randint(1, 1000000)
    print(f"\nGenerating board with seed {seed} and difficulty {difficulty}")
    
    # Generate puzzle with specified difficulty
    puzzle = Sudoku(3, seed=seed).difficulty(difficulty)  # 3x3 blocks = 9x9 grid
    
    print("\nGenerated puzzle:")
    puzzle.show()
    
    # Verify solvability and show solution
    solution = puzzle.solve()
    print("\nSolution:")
    solution.show()
    
    # Convert puzzle to our format (list of lists with 0 for empty cells)
    board = []
    for row in puzzle.board:
        board.append([int(cell) if cell is not None else 0 for cell in row])
    
    return board