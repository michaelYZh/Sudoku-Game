## This module provides functions that solve a sudoku board using optimized algorithms
## including backtracking, forward checking, and heuristics

from typing import List, Tuple, Optional, Set
import random
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CellOptions:
    """Represents the valid options for a cell and its degree (number of empty cells in same row/col/box)"""
    options: Set[int]
    degree: int = 0

class SudokuSolver:
    def __init__(self, board: List[List[int]]):
        self.board = board
        self.options = [[CellOptions(set()) for _ in range(9)] for _ in range(9)]
        self._initialize_options()
    
    def _initialize_options(self) -> None:
        """Initialize valid options for each empty cell"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.options[i][j].options = self._get_valid_options(i, j)
                    self.options[i][j].degree = self._calculate_degree(i, j)
    
    def _get_valid_options(self, row: int, col: int) -> Set[int]:
        """Get all valid numbers that can be placed in the given cell"""
        valid_nums = set(range(1, 10))
        
        # Check row
        for j in range(9):
            if self.board[row][j] in valid_nums:
                valid_nums.remove(self.board[row][j])
        
        # Check column
        for i in range(9):
            if self.board[i][col] in valid_nums:
                valid_nums.remove(self.board[i][col])
        
        # Check box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] in valid_nums:
                    valid_nums.remove(self.board[i][j])
        
        return valid_nums
    
    def _calculate_degree(self, row: int, col: int) -> int:
        """Calculate the degree of a cell (number of empty cells in same row/col/box)"""
        degree = 0
        
        # Count empty cells in row
        for j in range(9):
            if self.board[row][j] == 0 and j != col:
                degree += 1
        
        # Count empty cells in column
        for i in range(9):
            if self.board[i][col] == 0 and i != row:
                degree += 1
        
        # Count empty cells in box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == 0 and (i != row or j != col):
                    degree += 1
        
        return degree
    
    def _get_next_cell(self) -> Optional[Tuple[int, int]]:
        """Get the next cell to fill using heuristics"""
        min_options = float('inf')
        max_degree = -1
        candidates = []
        
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    num_options = len(self.options[i][j].options)
                    degree = self.options[i][j].degree
                    
                    if num_options < min_options or (num_options == min_options and degree > max_degree):
                        min_options = num_options
                        max_degree = degree
                        candidates = [(i, j)]
                    elif num_options == min_options and degree == max_degree:
                        candidates.append((i, j))
        
        return random.choice(candidates) if candidates else None
    
    def _get_next_value(self, row: int, col: int) -> Optional[int]:
        """Get the next value to try using heuristics"""
        if not self.options[row][col].options:
            return None
            
        # Calculate constraining count for each option
        constraining_counts = defaultdict(int)
        for num in self.options[row][col].options:
            # Count how many other cells would be constrained by this number
            for i in range(9):
                if i != col and self.board[row][i] == 0:
                    if num in self.options[row][i].options:
                        constraining_counts[num] += 1
                if i != row and self.board[i][col] == 0:
                    if num in self.options[i][col].options:
                        constraining_counts[num] += 1
            
            # Check box
            box_row, box_col = row // 3 * 3, col // 3 * 3
            for i in range(box_row, box_row + 3):
                for j in range(box_col, box_col + 3):
                    if (i != row or j != col) and self.board[i][j] == 0:
                        if num in self.options[i][j].options:
                            constraining_counts[num] += 1
        
        # If no constraints were found, just return any valid option
        if not constraining_counts:
            return random.choice(list(self.options[row][col].options))
            
        # Choose the value that constrains the fewest other cells
        min_constraints = min(constraining_counts.values())
        candidates = [num for num, count in constraining_counts.items() if count == min_constraints]
        return random.choice(candidates)
    
    def _update_options(self, row: int, col: int, num: int) -> None:
        """Update the options for all affected cells after placing a number"""
        # Update row
        for j in range(9):
            if self.board[row][j] == 0:
                self.options[row][j].options.discard(num)
                self.options[row][j].degree -= 1
        
        # Update column
        for i in range(9):
            if self.board[i][col] == 0:
                self.options[i][col].options.discard(num)
                self.options[i][col].degree -= 1
        
        # Update box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == 0:
                    self.options[i][j].options.discard(num)
                    self.options[i][j].degree -= 1
    
    def _restore_options(self, row: int, col: int, num: int) -> None:
        """Restore the options for all affected cells after backtracking"""
        # Restore row
        for j in range(9):
            if self.board[row][j] == 0:
                if self._is_valid(row, j, num):
                    self.options[row][j].options.add(num)
                self.options[row][j].degree += 1
        
        # Restore column
        for i in range(9):
            if self.board[i][col] == 0:
                if self._is_valid(i, col, num):
                    self.options[i][col].options.add(num)
                self.options[i][col].degree += 1
        
        # Restore box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == 0:
                    if self._is_valid(i, j, num):
                        self.options[i][j].options.add(num)
                    self.options[i][j].degree += 1
    
    def _is_valid(self, row: int, col: int, num: int) -> bool:
        """Check if a number can be placed in the given cell"""
        # Check row
        for j in range(9):
            if self.board[row][j] == num:
                return False
        
        # Check column
        for i in range(9):
            if self.board[i][col] == num:
                return False
        
        # Check box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == num:
                    return False
        
        return True
    
    def solve(self) -> bool:
        """Solve the Sudoku puzzle using backtracking with forward checking and heuristics"""
        cell = self._get_next_cell()
        if not cell:
            return True
        
        row, col = cell
        while True:
            num = self._get_next_value(row, col)
            if num is None:
                break
                
            self.board[row][col] = num
            self._update_options(row, col, num)
            
            if self.solve():
                return True
            
            self.board[row][col] = 0
            self._restore_options(row, col, num)
            self.options[row][col].options.remove(num)
        
        return False

def solve(board: List[List[int]]) -> bool:
    """
    Solve the Sudoku board using optimized backtracking with forward checking and heuristics.
    
    Args:
        board: A 9x9 grid representing the Sudoku board (0 for empty cells)
    
    Returns:
        bool: True if a solution was found, False otherwise
    
    Effects:
        Mutates the input board with the solution if one exists
    """
    solver = SudokuSolver(board)
    return solver.solve()