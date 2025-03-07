## This module provides functions that solve a sudoku board using optimized algorithms
## including backtracking, forward checking, and heuristics

from typing import List, Tuple, Optional, Set, Iterator
import random
from dataclasses import dataclass
from collections import defaultdict

@dataclass
class CellState:
    """Represents the valid options for a cell and its degree (number of empty cells in same row/col/box)"""
    options: Set[int]
    degree: int = -1

@dataclass
class SolveStep:
    """Represents a single step in the solving process"""
    row: int
    col: int
    value: int
    step_type: str  # "attempt", "success", "backtrack", 

class SudokuSolver:
    def __init__(self, board: List[List[int]]):
        self.board = board
        self.options = [[CellState(set()) for _ in range(9)] for _ in range(9)]
        self.last_backtrack = None  # Track the last backtracked cell (row, col)
        self._initialize_state()
    
    def _initialize_state(self) -> None:
        """Initialize valid options and degree for each empty cell"""
        for i in range(9):
            for j in range(9):
                if self.board[i][j] == 0:
                    self.options[i][j].options = self._get_valid_options(i, j)
                    self.options[i][j].degree = self._calculate_degree(i, j)
    
    def _get_valid_options(self, row: int, col: int) -> Set[int]:
        """Get all valid numbers that can be placed in the given empty cell"""
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
        """Calculate the degree of a an empty cell (number of empty cells in same row/col/box)"""
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
        """Get the next empty cell to fill using the Minimum Remaining Values (MRV) heuristic
        with Degree heuristic as a tie-breaker.
        
        MRV: Choose the cell with fewest valid options left
        Degree: Among cells with same number of options, choose the one that affects the most unfilled cells
        If multiple cells tie on both criteria, choose randomly among them.
        """
        min_options = 10  # Maximum possible options in Sudoku is 9
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
        """Get the next value to try using the Least Constraining Value heuristic.
        
        For each possible value, count how many options would be eliminated from other empty cells
        if this value were placed. Choose the value that constrains (eliminates options from) the
        fewest other cells. If multiple values tie, choose randomly among them.
        
        Returns None if no valid options remain for this cell.
        """
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
    
    def _update_cell_options(self, row: int, col: int, num: int) -> bool:
        """Remove the placed number from options of all affected empty cells and
        set the current cell's options to invalid state (empty set).
        
        Returns:
            bool: True if all affected cells still have at least one option,
                 False if any cell is left with no options
        """
        # Set current cell to invalid state (like initial filled cells)
        self.options[row][col].options = set()
        
        # Update row
        for j in range(9):
            if self.board[row][j] == 0:
                self.options[row][j].options.discard(num)
                if not self.options[row][j].options:
                    return False
        
        # Update column
        for i in range(9):
            if self.board[i][col] == 0:
                self.options[i][col].options.discard(num)
                if not self.options[i][col].options:
                    return False
        
        # Update box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == 0:
                    self.options[i][j].options.discard(num)
                    if not self.options[i][j].options:
                        return False
        
        return True

    def _update_cell_degrees(self, row: int, col: int) -> None:
        """Decrease the degree of all affected empty cells after filling a cell
        and set the current cell's degree to invalid state (-1)"""
        # Set current cell to invalid state (like initial filled cells)
        self.options[row][col].degree = -1
        
        # Update row
        for j in range(9):
            if self.board[row][j] == 0 and self.options[row][j].degree >= 0:
                self.options[row][j].degree -= 1
        
        # Update column
        for i in range(9):
            if self.board[i][col] == 0 and self.options[i][col].degree >= 0:
                self.options[i][col].degree -= 1
        
        # Update box
        box_row, box_col = row // 3 * 3, col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.board[i][j] == 0 and self.options[i][j].degree >= 0:
                    self.options[i][j].degree -= 1

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
    
    def solve(self) -> Iterator[SolveStep]:
        """Solve the Sudoku puzzle using backtracking with forward checking and heuristics"""
        cell = self._get_next_cell()
        print(f"Getting next cell: {cell}")  # Debug print
        if not cell:
            # We found a solution
            print("No more cells - solution found!")  # Debug print
            yield SolveStep(-1, -1, 0, "success")
            return
        
        row, col = cell
        while True:
            # Clear any previous backtrack visualization before trying new numbers
            if self.last_backtrack:
                yield SolveStep(self.last_backtrack[0], self.last_backtrack[1], 0, "clear")
                self.last_backtrack = None
                
            num = self._get_next_value(row, col)
            print(f"Trying cell ({row},{col}) with number: {num}")  # Debug print
            if num is None:
                # No more options left for this cell, backtrack
                print(f"No more options for ({row},{col}), backtracking")  # Debug print
                yield SolveStep(row, col, 0, "backtrack")
                self.last_backtrack = (row, col)  # Remember this cell for clearing later
                break

            if self._is_valid(row, col, num):
                # Try this number
                yield SolveStep(row, col, num, "attempt")
                
                # Backup current state
                curr_cell_options = self.options[row][col].options.copy()
                curr_cell_degree = self.options[row][col].degree
                global_cell_options = [[CellState(cell.options.copy(), cell.degree) for cell in row] 
                                    for row in self.options]
                
                # Set new state
                self.board[row][col] = num
                if self._update_cell_options(row, col, num):
                    self._update_cell_degrees(row, col)
                    
                    # Try to solve the rest of the board
                    solution_found = False
                    print(f"Recursing after placing {num} at ({row},{col})")  # Debug print
                    for step in self.solve():
                        yield step
                        if step.step_type == "success":
                            solution_found = True
                    
                    if solution_found:
                        print(f"Success propagated to ({row},{col}) with {num}")  # Debug print
                        yield SolveStep(row, col, num, "success")
                        return
                
                # If we get here, this number didn't work
                print(f"Number {num} didn't work at ({row},{col}), restoring state")  # Debug print
                self.board[row][col] = 0
                # Restore state from backup
                self.options = global_cell_options
                self.options[row][col].options = curr_cell_options
                self.options[row][col].degree = curr_cell_degree
            
            # Remove the number from options since it didn't lead to a solution
            self.options[row][col].options.remove(num)
        
        print(f"No solution found for ({row},{col})")  # Debug print
        return

def solve(board: List[List[int]]) -> Iterator[SolveStep]:
    """
    Solve the Sudoku board using optimized backtracking with forward checking and heuristics.
    
    Args:
        board: A 9x9 grid representing the Sudoku board (0 for empty cells)
    
    Returns:
        Iterator[SolveStep]: Iterator yielding each step of the solving process
    
    Effects:
        Mutates the input board with the solution if one exists
    """
    solver = SudokuSolver(board)
    result = solver.solve()
    if isinstance(result, bool):
        return iter([])  # Return empty iterator if result is boolean
    return result  # Return the iterator of steps
def _find_empty(board):
    """Find an empty cell in the board."""
    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == 0:
                return (i, j)
    return None

def _is_valid(board, row, col, num):
    """Check if a number is valid in a cell."""
    # Check row
    for x in range(len(board[0])):
        if board[row][x] == num:
            return False
    
    # Check column
    for x in range(len(board)):
        if board[x][col] == num:
            return False
    
    # Check box
    box_x = row // 3 * 3
    box_y = col // 3 * 3
    for i in range(3):
        for j in range(3):
            if board[box_x + i][box_y + j] == num:
                return False
    
    return True
