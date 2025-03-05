class Box:
    def __init__(self, value: int = 0, fixed: bool = False):
        self.value = value
        self.selected = False
        self.draft = set()
        self.fixed = fixed  # Whether this is a pre-filled cell
        
    def _draw(self, surface: pygame.Surface, x: int, y: int) -> None:
        """Draw the box."""
        # Draw background
        bg_color = Colors.FIXED_BG if self.fixed else Colors.BG
        if self.selected:
            bg_color = Colors.SELECTED_BG
        pygame.draw.rect(surface, bg_color, (x, y, CELL_SIZE, CELL_SIZE)) 