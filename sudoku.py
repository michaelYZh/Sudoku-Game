"""Main module for the Sudoku game GUI."""

import pygame
import time
from typing import List, Optional, Tuple, Dict, Set
from dataclasses import dataclass
from generate import generate_board, DIFFICULTY_MEDIUM, DIFFICULTY_EASY, DIFFICULTY_HARD, DIFFICULTY_EXPERT
from solver import solve
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, BG_COLOR, BOARD_SIZE,
    BORDER_THICK, BORDER_THIN, BORDER_COLOR,
    Colors, Positions, FONT_SIZE, SMALL_FONT_SIZE,
    SYSTEM_FONT, DRAFT_SHIFT, SOLVE_PAUSE_TIME,
    END_GAME_DELAY, GameState, Difficulty, BUTTON_PADDING,
    BUTTON_BORDER_RADIUS, BUTTON_FONT_SIZE, BOARD_START_X,
    BOARD_START_Y, CELL_SIZE, BOARD_WIDTH, BOARD_HEIGHT,
    BUTTON_WIDTH, BUTTON_HEIGHT, BOARD_FONT_SIZE
)

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
    draft: Set[int]
    selected: bool
    highlighted: bool = False

class Board:
    """Manages the Sudoku game board and its state."""
    
    def __init__(self, difficulty: int = DIFFICULTY_MEDIUM):
        self.width = BOARD_WIDTH
        self.height = BOARD_HEIGHT
        self.start_x = BOARD_START_X
        self.start_y = BOARD_START_Y
        self.boxes = self._create_boxes(difficulty)
        self.box_selected: Optional[Tuple[int, int]] = None
        self.time = 0
        self.start_time = None  # Initialize as None instead of current time
        self.incorrect_attempts = 0
        self.state = GameState.PLAYING
        self.font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)
        self.board_font = pygame.font.SysFont(SYSTEM_FONT, BOARD_FONT_SIZE)
        self.small_font = pygame.font.SysFont(SYSTEM_FONT, SMALL_FONT_SIZE)
        self.difficulty = difficulty
        self.conflict_cells = []
        self.conflict_timer = None
        
        # Create UI buttons with fixed size
        positions = Positions()
        self.new_game_button = Button("New Game", positions.NEW_GAME_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT))
        self.difficulty_buttons = {
            DIFFICULTY_EASY: Button("Easy", positions.EASY_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_MEDIUM: Button("Medium", positions.MEDIUM_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_HARD: Button("Hard", positions.HARD_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT)),
            DIFFICULTY_EXPERT: Button("Expert", positions.EXPERT_BUTTON, (BUTTON_WIDTH, BUTTON_HEIGHT))
        }
    
    def _create_boxes(self, difficulty: int) -> List[List[Box]]:
        """Create the initial board with boxes."""
        max_attempts = 5  # Maximum number of attempts to generate a valid board
        for _ in range(max_attempts):
            try:
                board = generate_board(difficulty)
                boxes = []
                for i in range(BOARD_SIZE):
                    row = []
                    for j in range(BOARD_SIZE):
                        value = board[i][j]
                        row.append(Box(i, j, value, value != 0, set(), False))
                    boxes.append(row)
                return boxes
            except Exception as e:
                print(f"Error generating board: {e}. Retrying...")
        
        # If we couldn't generate a valid board after max attempts,
        # fall back to an easier difficulty
        if difficulty > DIFFICULTY_EASY:
            print("Falling back to easier difficulty...")
            return self._create_boxes(difficulty - 50)
        else:
            raise RuntimeError("Could not generate a valid Sudoku board")
    
    def reset_game(self, difficulty: Optional[int] = None) -> None:
        """Reset the game with optional new difficulty."""
        if difficulty is not None:
            self.difficulty = difficulty
        self.boxes = self._create_boxes(self.difficulty)
        self.box_selected = None
        self.start_time = None  # Reset timer to None
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

    def select(self, row: int, col: int) -> None:
        """Select a box at the given position."""
        # Don't select if the cell is fixed (initial number)
        if self.boxes[row][col].fixed:
            return
            
        self._start_timer_if_not_started()  # Start timer on first selection
        if self.box_selected:
            self.boxes[self.box_selected[0]][self.box_selected[1]].selected = False
        self.box_selected = (row, col)
        self.boxes[row][col].selected = True
    
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
        
        # Check row
        for j in range(BOARD_SIZE):
            if self.boxes[row][j].value == value:
                conflicts.append((row, j))
        
        # Check column
        for i in range(BOARD_SIZE):
            if self.boxes[i][col].value == value:
                conflicts.append((i, col))
        
        # Check box
        box_row = row // 3 * 3
        box_col = col // 3 * 3
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.boxes[i][j].value == value:
                    conflicts.append((i, j))
        
        return conflicts

    def place_number(self, value: int) -> bool:
        """Place a number in the selected box. Returns True if placement was valid."""
        if self.box_selected and not self.boxes[self.box_selected[0]][self.box_selected[1]].fixed:
            row, col = self.box_selected
            box = self.boxes[row][col]
            
            # If the number is already there, clear it
            if box.value == value:
                box.value = 0
                return True
            
            if self._is_valid_placement(row, col, value):
                box.value = value
                box.draft.clear()
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
                box.selected = False
                self.box_selected = None
                return False
        return False
    
    def clear(self) -> None:
        """Clear the selected box."""
        if self.box_selected and not self.boxes[self.box_selected[0]][self.box_selected[1]].fixed:
            self.boxes[self.box_selected[0]][self.box_selected[1]].value = 0
            self.boxes[self.box_selected[0]][self.box_selected[1]].draft.clear()
    
    def _is_valid_placement(self, row: int, col: int, value: int) -> bool:
        """Check if a value can be placed at the given position."""
        # Check row
        for j in range(BOARD_SIZE):
            if self.boxes[row][j].value == value:
                return False
    
        # Check column
        for i in range(BOARD_SIZE):
            if self.boxes[i][col].value == value:
                return False

        # Check box
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
                if box.value == 0:
                    return False
        return True

    def solve(self) -> None:
        """Solve the current board using the solver."""
        # Clear selection before solving
        if self.box_selected:
            self.boxes[self.box_selected[0]][self.box_selected[1]].selected = False
            self.box_selected = None
        
        board = [[box.value for box in row] for row in self.boxes]
        if solve(board):
            # Animate the solution
            for i in range(BOARD_SIZE):
                for j in range(BOARD_SIZE):
                    if self.boxes[i][j].value != board[i][j]:
                        self.boxes[i][j].value = board[i][j]
                        self.boxes[i][j].draft.clear()
                        # Redraw after each number placement
                        self.draw(pygame.display.get_surface())
                        pygame.display.flip()
                        pygame.time.wait(50)  # 50ms delay between each number
            
            # Set state to completed
            self.state = GameState.COMPLETED
        else:
            self.state = GameState.ERROR
    
    def sketch(self, value: int) -> None:
        """Add or remove a draft value in the selected box."""
        if self.box_selected and not self.boxes[self.box_selected[0]][self.box_selected[1]].fixed:
            box = self.boxes[self.box_selected[0]][self.box_selected[1]]
            # Clear any existing value when adding drafts
            box.value = 0
            
            # If clicking the same number that's already drafted, remove it
            if value in box.draft:
                box.draft.clear()
            else:
                # Replace any existing draft with the new number
                box.draft.clear()
                box.draft.add(value)
    
    def try_place_draft(self) -> None:
        """Try to place the first draft number in the selected cell."""
        if self.box_selected:
            row, col = self.box_selected
            box = self.boxes[row][col]
            if box.draft:
                # Get the first draft number and try to place it
                num = min(box.draft)
                if not self.place_number(num):
                    # If placement fails, clear drafts
                    box.draft.clear()
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the board and its state on the screen."""
        screen.fill(BG_COLOR)
        
        # Draw boxes
        for i in range(BOARD_SIZE):
            for j in range(BOARD_SIZE):
                self._draw_box(screen, i, j)
        
        # Draw borders
        self._draw_borders(screen)
        
        # Draw game state
        self._draw_game_state(screen)
        
        # Draw UI buttons
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
    
    def _draw_box(self, screen: pygame.Surface, row: int, col: int) -> None:
        """Draw a single box on the screen."""
        box = self.boxes[row][col]
        x = self.start_x + col * CELL_SIZE
        y = self.start_y + row * CELL_SIZE
        
        # Draw box background - always show solved background if state is completed
        if self.state == GameState.COMPLETED:
            pygame.draw.rect(screen, Colors.SOLVED_BG, (x, y, CELL_SIZE, CELL_SIZE))
        else:
            # Draw base background first
            pygame.draw.rect(screen, BG_COLOR, (x, y, CELL_SIZE, CELL_SIZE))
            
            # Draw selection highlighting
            if box.selected:
                pygame.draw.rect(screen, Colors.SELECTED, (x, y, CELL_SIZE, CELL_SIZE))
            elif box.highlighted:
                pygame.draw.rect(screen, Colors.HIGHLIGHT, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw conflict highlighting
        if (row, col) in self.conflict_cells:
            pygame.draw.rect(screen, Colors.CONFLICT, (x, y, CELL_SIZE, CELL_SIZE))
        
        # Draw value
        if box.value != 0:
            color = Colors.FIXED if box.fixed else Colors.VALUE
            text = self.board_font.render(str(box.value), True, color)
            screen.blit(text, (x + (CELL_SIZE - text.get_width()) / 2,
                              y + (CELL_SIZE - text.get_height()) / 2))
        
        # Draw draft numbers
        for i, num in enumerate(sorted(box.draft)):
            text = self.small_font.render(str(num), True, Colors.DRAFT)
            screen.blit(text, (x + (i % 3) * (CELL_SIZE / 3) + DRAFT_SHIFT,
                              y + (i // 3) * (CELL_SIZE / 3) + DRAFT_SHIFT))
    
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
    
    def _draw_game_state(self, screen: pygame.Surface) -> None:
        """Draw the game state (time, incorrect attempts, etc.)."""
        # Draw time
        elapsed = int(time.time() - self.start_time) if self.start_time else 0
        time_text = self.font.render(f"Time: {elapsed}s", True, Colors.TIME)
        screen.blit(time_text, Positions.TIME)
        
        # Draw incorrect attempts
        incorrect_text = self.font.render(f"Mistakes: {self.incorrect_attempts}", True, Colors.INCORRECT)
        screen.blit(incorrect_text, Positions.MISTAKES)
        
        # Draw "Solved!" message when completed
        if self.state == GameState.COMPLETED:
            solved_text = self.font.render("Solved!", True, Colors.PROGRESS)
            # Calculate position to center between time and mistakes
            solved_x = self.start_x + (self.width - solved_text.get_width()) // 2
            solved_y = self.start_y + self.height + 15  # Same y-position as time and mistakes
            screen.blit(solved_text, (solved_x, solved_y))
        elif self.state == GameState.ERROR:
            self._draw_error_message(screen)
    
    def _draw_error_message(self, screen: pygame.Surface) -> None:
        """Draw the error message."""
        message = self.font.render("No Solution!", True, Colors.RESULT)
        screen.blit(message, (self.width / 2 - message.get_width() / 2, Positions.MESSAGE))

def main():
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sudoku")
    board = Board()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                
                # Check button clicks
                if board.new_game_button.is_clicked(pos):
                    board.reset_game()
                else:
                    # Check difficulty button clicks
                    for diff, button in board.difficulty_buttons.items():
                        if button.is_clicked(pos):
                            board.reset_game(diff)
                            break
                    else:
                        # Handle board clicks if no button was clicked
                        clicked = board.click(pos)
                        if clicked:
                            board.select(*clicked)
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.solve()
                    if board.state == GameState.ERROR:
                        # Show error message
                        board.draw(screen)
                        pygame.display.flip()
                        pygame.time.wait(1000)  # Show error for 1 second
                elif board.box_selected:  # Only check these keys if a cell is selected
                    if event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
                                   pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9]:
                        num = int(event.unicode)
                        # Always use draft mode for number entry
                        board.sketch(num)
                    elif event.key == pygame.K_RETURN:
                        # Only try to place number on Enter
                        board.try_place_draft()
                    elif event.key == pygame.K_BACKSPACE:
                        board.clear()
            
            # Handle conflict timer
            if hasattr(event, 'type') and event.type == board.conflict_timer:
                board.conflict_cells = []  # Clear conflicts
                pygame.time.set_timer(board.conflict_timer, 0)  # Stop timer
        
        board.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()