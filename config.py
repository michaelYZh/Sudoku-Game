"""Configuration settings for the Sudoku game."""

from dataclasses import dataclass
from typing import Tuple, List

# Button settings
BUTTON_WIDTH = 110  # Base width for all buttons
BUTTON_HEIGHT = 35
BUTTON_SPACING = 15
BUTTON_TOP = 15

# Calculate total width based on buttons
TOTAL_BUTTONS_WIDTH = (BUTTON_WIDTH * 5) + (BUTTON_SPACING * 4)  # 610 pixels

# Board settings
BOARD_SIZE = 9
BOARD_PADDING = 20  # Padding on each side of the board
CELL_SIZE = 68  # Make each cell 68x68 pixels (divisible by 9)
BOARD_WIDTH = CELL_SIZE * BOARD_SIZE  # 612 pixels (perfectly divisible)
BOARD_HEIGHT = BOARD_WIDTH

# Screen settings
SCREEN_WIDTH = BOARD_WIDTH + (BOARD_PADDING * 2)  # Add padding on both sides
SCREEN_HEIGHT = 725
BG_COLOR = (245, 245, 245)

# Calculate board position
BOARD_START_X = (SCREEN_WIDTH - BOARD_WIDTH) // 2  # Center horizontally
BOARD_START_Y = 65

# Border settings
BORDER_THICK = 2
BORDER_THIN = 1
BORDER_COLOR = (120, 120, 120)

# Colors
@dataclass
class Colors:
    # Main colors
    TIME = (100, 100, 100)
    INCORRECT = (200, 80, 80)
    DRAFT = (160, 160, 160)
    VALUE = (70, 130, 180)
    FIXED = (60, 60, 60)
    SELECTED = (230, 230, 255, 40)
    PROGRESS = (50, 205, 50)
    RESULT = (100, 100, 100)
    CONFLICT = (255, 200, 200, 40)  # Light red for conflicting cells
    SOLVED_BG = (220, 255, 220, 40)  # Light green for solved board
    
    # UI elements
    BUTTON_BG = (220, 220, 220)
    BUTTON_HOVER = (200, 200, 200)
    NEW_GAME_BUTTON = (100, 180, 255)  # Blue for new game
    NEW_GAME_HOVER = (80, 160, 235)
    SELECTED_DIFFICULTY = (150, 200, 150)  # Green for selected difficulty
    BUTTON_TEXT = (80, 80, 80)
    HIGHLIGHT = (255, 255, 230, 30)
    SAME_NUMBER = (240, 240, 255, 30)

@dataclass
class Positions:
    """Positions for UI elements."""
    
    @property
    def button_positions(self) -> List[Tuple[int, int]]:
        """Calculate evenly spaced button positions."""
        start_x = (SCREEN_WIDTH - TOTAL_BUTTONS_WIDTH) // 2  # Center all buttons
        return [
            (start_x + i * (BUTTON_WIDTH + BUTTON_SPACING), BUTTON_TOP)
            for i in range(5)
        ]
    
    @property
    def EASY_BUTTON(self) -> Tuple[int, int]:
        return self.button_positions[0]
    
    @property
    def MEDIUM_BUTTON(self) -> Tuple[int, int]:
        return self.button_positions[1]
    
    @property
    def HARD_BUTTON(self) -> Tuple[int, int]:
        return self.button_positions[2]
    
    @property
    def EXPERT_BUTTON(self) -> Tuple[int, int]:
        return self.button_positions[3]
    
    @property
    def NEW_GAME_BUTTON(self) -> Tuple[int, int]:
        return self.button_positions[4]
    
    # Game state positions - moved down by adding more padding
    TIME = (BOARD_START_X, BOARD_START_Y + BOARD_HEIGHT + 15)  # Match button-to-board spacing
    MISTAKES = (BOARD_START_X + BOARD_WIDTH - 100, BOARD_START_Y + BOARD_HEIGHT + 15)  # Right-aligned, accounting for text width
    RESULT_TIME = SCREEN_WIDTH // 2
    TOTAL_INCORRECT = SCREEN_WIDTH // 2
    MESSAGE = SCREEN_HEIGHT - 15  # Match top margin

# Font settings
BUTTON_FONT_SIZE = 20  # UI elements (buttons, time, mistakes)
BOARD_FONT_SIZE = 35  # Numbers in the Sudoku board
FONT_SIZE = 20  # Other UI text
SMALL_FONT_SIZE = 20  # Draft numbers
SYSTEM_FONT = "Arial"

# Game settings
DRAFT_SHIFT = 4
SOLVE_PAUSE_TIME = 10
END_GAME_DELAY = 5000
BUTTON_PADDING = 10
BUTTON_BORDER_RADIUS = 5

# Game states
class GameState:
    PLAYING = "playing"
    SOLVING = "solving"
    COMPLETED = "completed"
    ERROR = "error"

# Difficulty levels
class Difficulty:
    EASY = "Easy"
    MEDIUM = "Medium"
    HARD = "Hard"
    EXPERT = "Expert" 