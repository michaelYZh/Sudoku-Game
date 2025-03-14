"""Main module for the Sudoku game GUI."""

import pygame
import time
from typing import List, Optional, Tuple, Callable
from dataclasses import dataclass
from generate import DIFFICULTY_MEDIUM, DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_EXPERT, generate_board
from solver import solve, SolveStep
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, BOARD_SIZE,
    BORDER_THICK, BORDER_THIN, BORDER_COLOR,
    Colors, Positions, FONT_SIZE, SMALL_FONT_SIZE,
    SYSTEM_FONT, DRAFT_SHIFT, GameState, Difficulty, BUTTON_PADDING,
    BUTTON_BORDER_RADIUS, BUTTON_FONT_SIZE, BOARD_START_X,
    BOARD_START_Y, CELL_SIZE, BOARD_WIDTH, BOARD_HEIGHT,
    BUTTON_WIDTH, BUTTON_HEIGHT, BOARD_FONT_SIZE
)
from enum import Enum, auto

class CellState(Enum):
    """Represents the visual state of a cell."""
    NONE = auto()        # Normal state
    SELECTED = auto()    # User selected this cell
    ATTEMPT = auto()     # Currently trying a number
    SUCCESS = auto()     # Part of the solution
    BACKTRACK = auto()   # Backtracking from this cell
    CLEAR = auto()       # Clear any previous state

@dataclass
class Button:
    """Represents a clickable button in the UI."""
    text: str
    pos: Tuple[int, int]
    size: Tuple[int, int]
    font_size: int = BUTTON_FONT_SIZE
    padding: int = BUTTON_PADDING
    border_radius: int = BUTTON_BORDER_RADIUS
    
    def __post_init__(self):
        self.font = pygame.font.SysFont(SYSTEM_FONT, self.font_size)
        self.text_surface = self.font.render(self.text, True, Colors.BUTTON_TEXT)
        self.rect = pygame.Rect(
            self.pos[0], self.pos[1],
            self.size[0], self.size[1]
        )
    
    def draw(self, screen: pygame.Surface, color: Tuple[int, int, int]) -> None:
        """Draw the button on the screen with the specified color."""
        pygame.draw.rect(screen, color, self.rect, border_radius=self.border_radius)
        screen.blit(self.text_surface, (
            self.rect.centerx - self.text_surface.get_width() // 2,
            self.rect.centery - self.text_surface.get_height() // 2
        ))
    
    def is_clicked(self, pos: Tuple[int, int]) -> bool:
        """Check if the button was clicked."""
        return self.rect.collidepoint(pos)

@dataclass
class Box:
    """Represents a single cell in the Sudoku board."""
    row: int
    col: int
    value: int
    fixed: bool
    draft: Optional[int]  # None means no draft value
    state: CellState = CellState.NONE
    
    def clear_value(self) -> None:
        """Clear the value of this box."""
        self.value = 0
        self.draft = None
    
    def set_value(self, value: int) -> None:
        """Set the value of this box."""
        self.value = value
        self.draft = None
    
    def toggle_draft(self, value: int) -> None:
        """Toggle a draft value in this box."""
        self.value = 0  # Clear any existing value
        if self.draft == value:
            self.draft = None
        else:
            self.draft = value
    
    def is_empty(self) -> bool:
        """Check if this box is empty."""
        return self.value == 0
    
    def is_editable(self) -> bool:
        """Check if this box can be edited."""
        return not self.fixed

class Board:
    """Manages the Sudoku game board and its state."""
    
    def __init__(self, difficulty: float = DIFFICULTY_MEDIUM):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.start_x = BOARD_START_X
        self.start_y = BOARD_START_Y
        self.boxes = self._create_boxes(difficulty)
        self.box_selected: Optional[Tuple[int, int]] = None
        self.time = 0
        self.start_time = None
        self.incorrect_attempts = 0
        self.state = GameState.PLAYING
        self.font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)
        self.board_font = pygame.font.SysFont(SYSTEM_FONT, BOARD_FONT_SIZE)
        self.small_font = pygame.font.SysFont(SYSTEM_FONT, SMALL_FONT_SIZE)
        self.difficulty = difficulty
        self.conflict_cells = []
        self.conflict_timer = None
        self.animation_queue = []
        self.animation_speed = {
            "attempt": 100,  # ms - fast for attempts
            "success": 50,   # ms - very fast for successful placements
            "backtrack": 150 # ms - slightly slower for backtracking
        }
        self.current_step: Optional[SolveStep] = None
        self.solving_text = ""
        
        # Create UI buttons with fixed size
        positions = Positions()
        self.new_game_button = Button("New Game", positions.NEW_GAME_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.difficulty_buttons = {
            DIFFICULTY_EASY: Button("Easy", positions.EASY_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_MEDIUM: Button("Medium", positions.MEDIUM_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_HARD: Button("Hard", positions.HARD_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_EXPERT: Button("Expert", positions.EXPERT_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT))
        }
    
    def _create_boxes(self, difficulty: float) -> List[List[Box]]:
        """Create the initial board with boxes."""
        try:
            board = generate_board(difficulty)
            boxes = []
            for i in range(BOARD_SIZE):
                row = []
                for j in range(BOARD_SIZE):
                    value = board[i][j]
                    row.append(Box(i, j, value, value != 0, None, CellState.NONE))
                boxes.append(row)
            return boxes
        except Exception as e:
            print(f"Error generating board: {e}")
            # If we get here, try with an easier difficulty
            if difficulty > DIFFICULTY_EASY:
                print("Falling back to easier difficulty...")
                return self._create_boxes(difficulty - 0.1)
            else:
                raise RuntimeError("Could not generate a valid Sudoku board")
    
    def reset_game(self, difficulty: Optional[float] = None) -> None:
        """Reset the game with optional new difficulty."""
        print("\nResetting game...")
        if difficulty is not None:
            print(f"Changing difficulty from {self.difficulty} to {difficulty}")
            self.difficulty = difficulty
        else:
            print(f"Keeping current difficulty: {self.difficulty}")
        
        self.boxes = self._create_boxes(self.difficulty)
        self.box_selected = None
        self.start_time = None
        self.incorrect_attempts = 0
        self.state = GameState.PLAYING
    
    def get_difficulty_text(self) -> str:
        """Get the current difficulty level as text."""
        if self.difficulty == DIFFICULTY_EASY:
            return Difficulty.EASY
        elif self.difficulty == DIFFICULTY_MEDIUM:
            return Difficulty.MEDIUM
        elif self.difficulty == DIFFICULTY_HARD:
            return Difficulty.HARD
        else:
            return Difficulty.EXPERT
    
    def cycle_difficulty(self) -> None:
        """Cycle through difficulty levels."""
        difficulties = [DIFFICULTY_EASY, DIFFICULTY_MEDIUM, DIFFICULTY_HARD, DIFFICULTY_EXPERT]
        current_index = difficulties.index(self.difficulty)
        next_index = (current_index + 1) % len(difficulties)
        self.reset_game(difficulties[next_index])
    
    def _start_timer_if_not_started(self):
        """Start the timer if it hasn't been started yet."""
        if self.start_time is None:
            self.start_time = time.time()

    def get_selected_box(self) -> Optional[Box]:
        """Get the currently selected box, if any."""
        if self.box_selected:
            row, col = self.box_selected
            return self.boxes[row][col]
        return None
    
    def for_each_box(self, callback: Callable[[Box], None]) -> None:
        """Apply a function to each box on the board."""
        for row in self.boxes:
            for box in row:
                callback(box)
    
    def for_each_box_with_coords(self, callback: Callable[[Box, int, int], None]) -> None:
        """Apply a function to each box on the board with its coordinates."""
        for i, row in enumerate(self.boxes):
            for j, box in enumerate(row):
                callback(box, i, j)

    def select(self, row: int, col: int) -> None:
        """Select a box at the given position."""
        # Don't select if the cell is fixed (initial number)
        if self.boxes[row][col].fixed:
            return
            
        self._start_timer_if_not_started()  # Start timer on first selection
        if self.box_selected:
            self.boxes[self.box_selected[0]][self.box_selected[1]].state = CellState.NONE
        self.box_selected = (row, col)
        self.boxes[row][col].state = CellState.SELECTED
    
    def click(self, pos: Tuple[int, int]) -> Optional[Tuple[int, int]]:
        """Handle a click event and return the clicked position if valid."""
        x, y = pos[0] - self.start_x, pos[1] - self.start_y
        if 0 <= x < self.width and 0 <= y < self.height:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            return (int(row), int(col))
        return None
    
    def _find_conflicts(self, row: int, col: int, value: int) -> List[Tuple[int, int]]:
        """Find all cells that conflict with the attempted placement."""
        conflicts = []
        
        # Check row conflicts
        row_conflicts = self._find_row_conflicts(row, value)
        conflicts.extend(row_conflicts)
        
        # Check column conflicts
        col_conflicts = self._find_column_conflicts(col, value)
        conflicts.extend(col_conflicts)
        
        # Check box conflicts
        box_conflicts = self._find_box_conflicts(row, col, value)
        conflicts.extend(box_conflicts)
        
        return conflicts
    
    def _find_row_conflicts(self, row: int, value: int) -> List[Tuple[int, int]]:
        """Find conflicts in the given row."""
        conflicts = []
        for j in range(BOARD_SIZE):
            if self.boxes[row][j].value == value:
                conflicts.append((row, j))
        return conflicts
    
    def _find_column_conflicts(self, col: int, value: int) -> List[Tuple[int, int]]:
        """Find conflicts in the given column."""
        conflicts = []
        for i in range(BOARD_SIZE):
            if self.boxes[i][col].value == value:
                conflicts.append((i, col))
        return conflicts
    
    def _find_box_conflicts(self, row: int, col: int, value: int) -> List[Tuple[int, int]]:
        """Find conflicts in the 3x3 box containing the given cell."""
        conflicts = []
        box_row = row // 3 * 3
        box_col = col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.boxes[i][j].value == value:
                    conflicts.append((i, j))
        return conflicts

    def place_number(self, value: int) -> bool:
        """Place a number in the selected box. Returns True if placement was valid."""
        selected_box = self.get_selected_box()
        if selected_box and selected_box.is_editable():
            row, col = self.box_selected
            
            # If the number is already there, clear it
            if selected_box.value == value:
                selected_box.clear_value()
                return True
            
            if self._is_valid_placement(row, col, value):
                selected_box.set_value(value)
                # Check if the board is now complete (only for manual solving)
                if self.state == GameState.PLAYING and self.is_finished():
                    self.state = GameState.COMPLETED
                    # Mark all non-fixed cells as successful immediately for manual completion
                    self.for_each_box(lambda box: setattr(box, 'state', CellState.SUCCESS) if not box.fixed else None)
                return True
            else:
                # Find and highlight conflicting cells
                self.conflict_cells = self._find_conflicts(row, col, value)
                # Start timer to clear highlights
                if self.conflict_timer:
                    pygame.time.set_timer(self.conflict_timer, 0)  # Cancel existing timer
                self.conflict_timer = pygame.USEREVENT + 1
                pygame.time.set_timer(self.conflict_timer, 1000)  # 1 second delay
                
                # Invalid placement - increment mistakes and reset selection
                self.incorrect_attempts += 1
                selected_box.state = CellState.NONE
                self.box_selected = None
                return False
        return False
    
    def clear(self) -> None:
        """Clear the selected box."""
        selected_box = self.get_selected_box()
        if selected_box and selected_box.is_editable():
            selected_box.clear_value()
    
    def _is_valid_placement(self, row: int, col: int, value: int) -> bool:
        """Check if a value can be placed at the given position."""
        # Check row
        if not self._is_valid_in_row(row, value):
            return False
    
        # Check column
        if not self._is_valid_in_column(col, value):
            return False

        # Check box
        if not self._is_valid_in_box(row, col, value):
            return False

        return True
    
    def _is_valid_in_row(self, row: int, value: int) -> bool:
        """Check if a value can be placed in the given row."""
        for j in range(BOARD_SIZE):
            if self.boxes[row][j].value == value:
                return False
        return True
    
    def _is_valid_in_column(self, col: int, value: int) -> bool:
        """Check if a value can be placed in the given column."""
        for i in range(BOARD_SIZE):
            if self.boxes[i][col].value == value:
                return False
        return True
    
    def _is_valid_in_box(self, row: int, col: int, value: int) -> bool:
        """Check if a value can be placed in the 3x3 box containing the given cell."""
        box_row = row // 3 * 3
        box_col = col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.boxes[i][j].value == value:
                    return False
        return True

    def is_finished(self) -> bool:
        """Check if the board is complete and valid."""
        for row in self.boxes:
            for box in row:
                if box.is_empty():
                    return False
        return True

    def solve(self) -> None:
        """Solve the current board using the solver with animation."""
        # Clear selection before solving
        if self.box_selected:
            self.boxes[self.box_selected[0]][self.box_selected[1]].state = CellState.NONE
            self.box_selected = None
        
        board = [[box.value for box in row] for row in self.boxes]
        self.state = GameState.SOLVING
        
        # Get all solving steps
        try:
            self.animation_queue = list(solve(board))
            if self.animation_queue:
                self._animate_next_step()
            else:
                self.state = GameState.ERROR
        except StopIteration:
            self.state = GameState.ERROR
    
    def _animate_next_step(self) -> None:
        """Process the next step in the solving animation."""
        if not self.animation_queue:
            self._handle_animation_completion()
            return
        
        self.current_step = self.animation_queue.pop(0)
        
        # Handle special success case (recursion end signal)
        if self._is_recursion_end_success_signal():
            self._handle_recursion_end_success_signal()
            return
        
        # Update the board based on step type
        self._update_board_for_animation_step()
    
    def _all_cells_successful(self) -> bool:
        """Check if all non-fixed cells are marked as successful."""
        for row in self.boxes:
            for box in row:
                if not box.fixed and box.value != 0 and box.state != CellState.SUCCESS:
                    return False
        return True

    def _handle_animation_completion(self) -> None:
        """Handle the completion of the animation sequence."""
        # Only mark completion if we're in solving state
        if self.state == GameState.SOLVING:
            # Check if the board is complete
            if self.is_finished():
                # Check if all cells are already marked as successful
                if not self._all_cells_successful():
                    # Mark any remaining non-fixed cells as successful
                    self.for_each_box(lambda box: setattr(box, 'state', CellState.SUCCESS) 
                                     if not box.fixed and box.state != CellState.SUCCESS else None)
                
                self.state = GameState.COMPLETED
                self.solving_text = "Solved!"
    
    def _is_recursion_end_success_signal(self) -> bool:
        """Check if the current step is the recursion completion signal."""
        return (self.current_step.step_type == "success" and 
                self.current_step.row == -1 and 
                self.current_step.col == -1)
    
    def _handle_recursion_end_success_signal(self) -> None:
        """Handle the recursion completion signal.
        
        This is not actually the final success, but rather indicates that
        the recursion has reached the end case and is now propagating back up.
        We don't need to do anything special here, just continue with the animation.
        """
        # We don't mark cells as successful here, as the success will propagate
        # through individual success steps for each cell
        pygame.time.set_timer(pygame.USEREVENT + 2, self.animation_speed["success"])
    
    def _update_board_for_animation_step(self) -> None:
        """Update the board based on the current animation step."""
        row, col = self.current_step.row, self.current_step.col
        
        if self.current_step.step_type == "attempt":
            self._handle_attempt_step(row, col)
        elif self.current_step.step_type == "success":
            self._handle_success_step(row, col)
        elif self.current_step.step_type == "clear":
            self._handle_clear_step(row, col)
        else:  # backtrack
            self._handle_backtrack_step(row, col)
    
    def _handle_attempt_step(self, row: int, col: int) -> None:
        """Handle an attempt step in the animation."""
        self.boxes[row][col].value = self.current_step.value
        self.boxes[row][col].state = CellState.ATTEMPT
        self.solving_text = f"Trying {self.current_step.value} at ({row+1},{col+1})"
        self._set_animation_timer("attempt")
    
    def _handle_success_step(self, row: int, col: int) -> None:
        """Handle a success step in the animation."""
        # Only update if this is a valid cell (not the special -1,-1 signal)
        if row >= 0 and col >= 0:
            self.boxes[row][col].set_value(self.current_step.value)
            self.boxes[row][col].state = CellState.SUCCESS
            self.solving_text = f"Placed {self.current_step.value} at ({row+1},{col+1})"
            
            # Check if the board is now complete after this success step
            if self.is_finished():
                # Check if all cells are already marked as successful
                if self._all_cells_successful():
                    self.state = GameState.COMPLETED
                    self.solving_text = "Solved!"
        
        self._set_animation_timer("success")
    
    def _handle_clear_step(self, row: int, col: int) -> None:
        """Handle a clear step in the animation."""
        self.boxes[row][col].state = CellState.NONE
        self._set_animation_timer("backtrack")  # Use backtrack timing
    
    def _handle_backtrack_step(self, row: int, col: int) -> None:
        """Handle a backtrack step in the animation."""
        self.boxes[row][col].clear_value()
        self.boxes[row][col].state = CellState.BACKTRACK
        self.solving_text = f"Backtracking from ({row+1},{col+1})"
        self._set_animation_timer("backtrack")
    
    def _set_animation_timer(self, step_type: str) -> None:
        """Set the timer for the next animation step."""
        pygame.time.set_timer(pygame.USEREVENT + 2, self.animation_speed[step_type])
    
    def sketch(self, value: int) -> None:
        """Add or remove a draft value in the selected box."""
        selected_box = self.get_selected_box()
        if selected_box and selected_box.is_editable():
            selected_box.toggle_draft(value)
    
    def try_place_draft(self) -> None:
        """Try to place the draft number in the selected cell."""
        selected_box = self.get_selected_box()
        if selected_box and selected_box.draft is not None:
            if not self.place_number(selected_box.draft):
                # If placement fails, clear draft
                selected_box.draft = None
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the board and its state on the screen."""
        screen.fill(BG_COLOR)
        
        # Draw boxes
        self.for_each_box_with_coords(lambda box, i, j: self._draw_box(screen, i, j))
        
        # Draw borders
        self._draw_borders(screen)
        
        # Draw game state
        self._draw_game_state(screen)
        
        # Draw UI buttons
        self._draw_buttons(screen)
    
    def _draw_buttons(self, screen: pygame.Surface) -> None:
        """Draw all UI buttons."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Draw new game button
        hover = self.new_game_button.is_clicked(mouse_pos)
        color = Colors.NEW_GAME_HOVER if hover else Colors.NEW_GAME_BUTTON
        self.new_game_button.draw(screen, color)
        
        # Draw difficulty buttons
        for diff, button in self.difficulty_buttons.items():
            hover = button.is_clicked(mouse_pos)
            if diff == self.difficulty:
                color = Colors.SELECTED_DIFFICULTY
            else:
                color = Colors.BUTTON_HOVER if hover else Colors.BUTTON_BG
            button.draw(screen, color)
    
    def _get_box_background_color(self, box: Box) -> Optional[Tuple[int, int, int, int]]:
        """Get the background color for a box based on its state."""
        if self.state == GameState.SOLVING:
            if box.state == CellState.ATTEMPT:
                return Colors.ATTEMPT
            elif box.state == CellState.SUCCESS:
                return Colors.SOLVED_BG
            elif box.state == CellState.BACKTRACK:
                return Colors.CONFLICT
        elif self.state == GameState.COMPLETED:
            # Show all cells in green when completed
            return Colors.SOLVED_BG
        elif box.state == CellState.SELECTED:
            return Colors.SELECTED
        return None
    
    def _draw_box(self, screen: pygame.Surface, row: int, col: int) -> None:
        """Draw a single box on the screen."""
        box = self.boxes[row][col]
        x = self.start_x + col * CELL_SIZE
        y = self.start_y + row * CELL_SIZE
        
        # Draw box background
        pygame.draw.rect(screen, BG_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw cell state background
        bg_color = self._get_box_background_color(box)
        if bg_color:
            pygame.draw.rect(screen, bg_color, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw conflict highlighting
        if (row, col) in self.conflict_cells:
            pygame.draw.rect(screen, Colors.CONFLICT, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Always draw the value last, on top of any background
        if box.value != 0:
            color = Colors.FIXED if box.fixed else Colors.VALUE
            text = self.board_font.render(str(box.value), True, color)
            screen.blit(text, (x + (CELL_SIZE - text.get_width()) / 2,
                              y + (CELL_SIZE - text.get_height()) / 2))
        
        # Draw draft number
        if box.draft is not None:
            text = self.small_font.render(str(box.draft), True, Colors.DRAFT)
            screen.blit(text, (x + DRAFT_SHIFT, y + DRAFT_SHIFT))
    
    def _draw_borders(self, screen: pygame.Surface) -> None:
        """Draw the board borders."""
        # Draw the outer border first
        outer_rect = pygame.Rect(
            self.start_x, self.start_y,
            self.width, self.height
        )
        pygame.draw.rect(screen, BORDER_COLOR, outer_rect, BORDER_THICK)
        
        # Draw inner vertical lines
        for i in range(1, BOARD_SIZE):
            thickness = BORDER_THICK if i % 3 == 0 else BORDER_THIN
            x = self.start_x + i * CELL_SIZE
            # Adjust line endpoints to stay within the outer border
            pygame.draw.line(screen, BORDER_COLOR,
                           (x, self.start_y + BORDER_THICK // 2),  # Start inside the top border
                           (x, self.start_y + self.height - BORDER_THICK // 2),  # End inside the bottom border
                           thickness)
        
        # Draw inner horizontal lines
        for i in range(1, BOARD_SIZE):
            thickness = BORDER_THICK if i % 3 == 0 else BORDER_THIN
            y = self.start_y + i * CELL_SIZE
            # Adjust line endpoints to stay within the outer border
            pygame.draw.line(screen, BORDER_COLOR,
                           (self.start_x + BORDER_THICK // 2, y),  # Start inside the left border
                           (self.start_x + self.width - BORDER_THICK // 2, y),  # End inside the right border
                           thickness)
    
    def _draw_status_text(self, screen: pygame.Surface, text: str, color: Tuple[int, int, int], position: Tuple[int, int]) -> None:
        """Draw status text on the screen."""
        text_surface = self.font.render(text, True, color)
        screen.blit(text_surface, position)
    
    def _draw_game_state(self, screen: pygame.Surface) -> None:
        """Draw the game state (time, incorrect attempts, etc.)."""
        # Draw time
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        self._draw_status_text(screen, f"Time: {elapsed}s", Colors.TIME, Positions.TIME)
        
        # Draw incorrect attempts
        self._draw_status_text(screen, f"Mistakes: {self.incorrect_attempts}", Colors.INCORRECT, Positions.MISTAKES)
        
        # Calculate center position for status messages
        center_x = self.start_x + (self.width - 100) // 2  # Approximate width for text
        status_y = self.start_y + self.height + 15
        
        # Draw solving status text during animation
        if self.state == GameState.SOLVING and self.solving_text:
            status_text = self.font.render(self.solving_text, True, Colors.TIME)
            # Calculate position to center the text
            text_x = self.start_x + (self.width - status_text.get_width()) // 2
            screen.blit(status_text, (text_x, status_y))
        elif self.state == GameState.COMPLETED:
            solved_text = self.font.render("Solved!", True, Colors.PROGRESS)
            text_x = self.start_x + (self.width - solved_text.get_width()) // 2
            screen.blit(solved_text, (text_x, status_y))
        elif self.state == GameState.ERROR:
            self._draw_error_message(screen)
    
    def _draw_error_message(self, screen: pygame.Surface) -> None:
        """Draw the error message."""
        error_text = self.font.render("No Solution!", True, Colors.INCORRECT)
        # Calculate position to center the text
        error_x = self.start_x + (self.width - error_text.get_width()) // 2
        error_y = self.start_y + self.height + 15
        screen.blit(error_text, (error_x, error_y))

def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sudoku")
    board = Board()
    running = True
    
    def handle_mouse_click(pos):
        """Handle mouse click events."""
        # Check button clicks
        if board.new_game_button.is_clicked(pos):
            board.reset_game()
            return True
        
        # Check difficulty button clicks
        for diff, button in board.difficulty_buttons.items():
            if button.is_clicked(pos):
                board.reset_game(diff)
                return True
        
        # Handle board clicks if no button was clicked
        clicked = board.click(pos)
        if clicked:
            board.select(*clicked)
            return True
        
        return False
    
    def handle_key_press(key, unicode_char):
        """Handle keyboard press events."""
        if key == pygame.K_SPACE:
            board.solve()
            return True
        
        if not board.box_selected:
            return False
            
        if key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                 pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
            num = int(unicode_char)
            board.sketch(num)
            return True
        elif key == pygame.K_RETURN:
            board.try_place_draft()
            return True
        elif key == pygame.K_BACKSPACE:
            board.clear()
            return True
        
        return False
    
    def handle_timer_events(event):
        """Handle timer-based events."""
        # Handle animation timer
        if event.type == pygame.USEREVENT + 2 and board.state == GameState.SOLVING:
            board._animate_next_step()
            return True
        
        # Handle conflict timer
        if hasattr(event, 'type') and event.type == board.conflict_timer:
            board.conflict_cells = []  # Clear conflicts
            pygame.time.set_timer(board.conflict_timer, 0)  # Stop timer
            return True
        
        return False
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_mouse_click(pygame.mouse.get_pos())
            
            elif event.type == pygame.KEYDOWN:
                handle_key_press(event.key, event.unicode)
            
            else:
                handle_timer_events(event)
        
        board.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()