## This module provides the GUI for the susoku game

import pygame
from generate import generate_board
import time

SCREEN_WIDTH = 540
SCREEN_HEIGHT = 600
BG_COLOR = (255, 255, 255)
BOARDER_THICK_WIDTH = 4
BOARDER_THIN_WIDTH = 1
BOARDER_COLOR = (0, 0, 0)

TIME_COLOR = (0, 0, 0)
TIME_POS = (380, 560)

CROSS_COLOR = (255, 0, 0)
CROSS_POS = (20, 560)
INCRCT_COLOR = (0, 0, 0)
INCRCT_POS = (40, 560)

FONT_SIZE = 40
SYSTEM_FONT = "comicsans"

BOX_BOARDER_WIDTH = 4
DRAFT_COLOR = (128, 128, 128)
VALUE_COLOR = (75, 156, 211)
FIXED_COLOR = (0, 0, 0)
SELECTED_COLOR = (255, 0, 0)
PROGRESS_COLOR = (0, 255, 0)
DRAFT_SHIFT = 5

SOLVE_PAUSE_TIME = 10

END_GAME_DELAY = 5000
RESULT_COLOR = (0, 0, 0)
RESULT_TIME_Y = 200
TOTAL_INCRT_Y = 300
MSG_Y = 400

rows = 9
cols = 9

class Board(object):
    '''
    Fields:
        width (Nat)
        height (Nat)
        boxes (listof Box)
        box_selected (tupleof Nat Nat)

    Requires:
        0 < width, height
        boxes is a valid sudoku grid with 81 boxes
        values in box_selected < 9
    '''

    box_dim = SCREEN_WIDTH / cols

    def __init__(self, width, height):
        '''
        Constructor: create a Board object by calling Board(width, height)

        Effects: mutates self

        __init__: Board, Nat, Nat -> None
        Requires: width, height > 0
        '''
        self.width = width
        self.height = height
        self.boxes = []
        self.box_selected = None

    def init_boxes(self):
        '''
        Initalizes boxes for the sudoku board

        Effects: mutates self

        init_boxes: Board -> None
        '''
        bo = generate_board()
        for i in range(len(bo)):
            col = []
            for j in range(len(bo[0])):
                if bo[i][j] == 0:
                    col.append(Box(bo[i][j], j * self.box_dim, 
                                    i * self.box_dim, False))
                else:
                    col.append(Box(bo[i][j], j * self.box_dim, 
                                    i * self.box_dim, True))
            self.boxes.append(col)

    def select_box(self, row, col):
        '''
        Set the selected box to be the one on position (row, col)

        Effects: mutates self

        select_box: Board Nat Nat -> None
        Requires: row, col < 9
        '''
        if not self.boxes[row][col].fixed:
            if self.box_selected:
                r, c = self.box_selected
                self.boxes[r][c].selected = False
            self.boxes[row][col].selected = True
            self.box_selected = (row, col)

    def set_draft(self, num):
        '''
        Set the draft for the selected box to be num

        Effects: mutates self

        set_draft: Board Nat -> None
        Requires: 0 < num <= 9
                  a box is selected (not None)
        '''
        self.boxes[self.box_selected[0]][self.box_selected[1]].draft = num

    def clear_draft(self):
        '''
        Clears the draft for the selected box

        Effects: mutates self

        clear_draft: Board -> None
        Requires: a box is selected (not None)
        '''
        self.set_draft(0)

    def find_empty(self):
        '''
        Finds the position of the next box that is unfilled

        find_empty: Board -> (tupleof Nat Nat)
        '''
        for i in range(len(self.boxes)):
            for j in range(len(self.boxes[0])):
                if self.boxes[i][j].num == 0:
                    return (i, j)

    def is_valid_board(self, num, pos):
        '''
        Determines if the board is a valid sudoku board when num is added at pos

        is_valid_board: Board Nat (tupleof Nat Nat) -> Bool
        Requires: 0 < num <= 9
                  pos is a valid position
        '''
        for i in range(len(self.boxes[0])):
            if self.boxes[pos[0]][i].num == num and pos[1] != i:
                return False
    
        for i in range(len(self.boxes)):
            if self.boxes[i][pos[1]].num == num and pos[0] != i:
                return False

        box_cow = pos[1] // 3
        box_row = pos[0] // 3

        for i in range(box_row * 3, box_row * 3 + 3):
            for j in range(box_cow * 3, box_cow * 3 + 3):
                if self.boxes[i][j].num == num and (i, j) != pos:
                    return False

        return True

    def solve_board(self):
        '''
        Solves the sudoku board

        Effects: mutates self

        solve_board: Board -> Bool
        '''
        find = self.find_empty()
        if not find:
            return True

        row, col = find
        for num in range(1, 10):
            if self.is_valid_board(num, (row, col)):
                self.boxes[row][col].num = num
                if self.solve_board():
                    return True
        self.boxes[row][col].num = 0
        return False

    def copy_board(self):
        '''
        Returns a board with the same dimensions and the same progress
            (only has the same numbers not the drafts)

        copy_board: Board -> Board
        '''
        duplicate = Board(self.width, self.height)
        og = self.boxes
        for i in range(len(og)):
            col = []
            for j in range(len(og[0])):
                col.append(Box(og[i][j].num, 0, 0, True))
            duplicate.boxes.append(col)
        return duplicate

    def set_num(self):
        '''
        Places the draft number into the board if it can potentially solve
            the board

        Effects: may mutate self

        set_num: Board -> (anyof None Bool)
        '''
        row, col = self.box_selected
        draft = self.boxes[row][col].draft
        if draft != 0:
            if self.boxes[row][col].num == 0:
                if self.is_valid_board(draft, self.box_selected):
                    self.boxes[row][col].num = draft
                    dup = self.copy_board()
                    if dup.solve_board():
                        self.boxes[row][col].draft = 0
                        return True
                self.boxes[row][col].num = 0
                self.boxes[row][col].draft = 0
                return False
    
    def is_completed(self):
        '''
        Checks if the sudoku board is completed/the game is over

        is_completed: Board -> Bool
        '''
        for i in range(len(self.boxes)):
            for j in range(len(self.boxes[0])):
                if self.boxes[i][j].num == 0:
                    return False
        return True

    def mouse_selection(self, pos):
        '''
        Returns the box selected by the mouse based on pos

        mouse_selection: Board (tupleof Nat Nat) -> 
                                                (anyof None (tupleof Nat Nat))
        Requires: 0 <= pos[0] <= self.width
                  0 <= pos[1]
        '''
        if 0 <= pos[1] <= self.height:
            return (int(pos[1] // self.box_dim), int(pos[0] // self.box_dim))
        return None

    def draw_lines(self, win):
        '''
        Draws the boarder lines for the sudoku board on win

        Effects: mutates win

        draw_lines: Board Window -> None
        '''
        for i in range(rows):
            if i % 3 == 0 and i:
                line_width = BOARDER_THICK_WIDTH
            else:
                line_width = BOARDER_THIN_WIDTH
            pygame.draw.line(win, BOARDER_COLOR, (0, i * self.box_dim),
                             (self.width, self.box_dim * i), line_width)
            pygame.draw.line(win, BOARDER_COLOR, (i * self.box_dim, 0),
                             (i * self.box_dim, self.height), line_width)
        pygame.draw.line(win, BOARDER_COLOR, (0, self.width), 
                         (self.width, self.width), BOARDER_THICK_WIDTH)
        pygame.draw.line(win, BOARDER_COLOR, (self.width, 0), 
                         (self.width, self.width), BOARDER_THICK_WIDTH) 
    
    def draw(self, win):
        '''
        Draws the sudoku board on win

        Effects: mutates win

        draw: Board Window -> None
        '''
        self.draw_lines(win)         
        for i in range(rows):
            for j in range(cols):
                self.boxes[i][j].draw(win)

    def print_board_num(self):
        '''
        Prints the numbers in the sudoku board

        Effects: printing to screen

        print_board_num: Board -> None
        '''
        for i in range(len(self.boxes)):
            if i % 3 == 0 and i:
                print("- - - - - - - - - - -")
            for j in range(len(self.boxes[0])):
                if j % 3 == 0 and j:
                    print("| ", end="")
                print(str(self.boxes[i][j].num) + " ", end="")
                if j == 8:
                    print("")

    def print_board_draft(self):
        '''
        Prints the drafts in the sudoku board

        Effects: printing to screen

        print_board_num: Board -> None
        '''
        for i in range(len(self.boxes)):
            if i % 3 == 0 and i:
                print("- - - - - - - - - - -")
            for j in range(len(self.boxes[0])):
                if j % 3 == 0 and j:
                    print("| ", end="")
                print(str(self.boxes[i][j].draft) + " ", end="")
                if j == 8:
                    print("")

    def redraw_select(self, win):
        '''
        Clears the graphic for the selection of a box on win

        Effects: mutates self, win
                 print to pygame window

        redraw_selecr: Board Window -> None
        '''
        if self.box_selected:
            row, col = self.box_selected
            self.selected = None
            self.boxes[row][col].selected = False
            pygame.draw.rect(win, BG_COLOR, (0, 0, SCREEN_WIDTH, SCREEN_WIDTH), 0)
            self.draw_lines(win)         
            for i in range(rows):
                for j in range(cols):
                    self.boxes[i][j].draw_num_only(win)
            pygame.display.update()


    def visualize_solve(self, win):
        '''
        Draws the solving process of the sudoku board on win

        Effects: mutates self, win
                 print to pygame window

        visualize_solve: Board Window -> None
        '''
        find = self.find_empty()
        if not find:
            return True

        row, col = find
        for num in range(1, 10):
            if self.is_valid_board(num, (row, col)):
                self.boxes[row][col].num = num
                self.boxes[row][col].draw_solve(win, False)
                pygame.display.update()
                pygame.time.delay(SOLVE_PAUSE_TIME)

                if self.visualize_solve(win):
                    return True

                self.boxes[row][col].num = 0
                self.boxes[row][col].draw_solve(win, True)
                pygame.display.update()
                pygame.time.delay(SOLVE_PAUSE_TIME)

        return False


class Box(object):
    '''
    Fields:
        num (Nat)
        draft (Nat)
        x (Float)
        y (Float)
        fixed (Bool)
        selected (Bool)

    Requires: 0 <= num, draft <= 9
              0 <= x, y <= SCREEN_WIDTH - side
    '''

    side = SCREEN_WIDTH / cols

    def __init__(self, num, x, y, fixed):
        '''
        Constructor: create a Box object by calling Box(num, x, y, fixed)

        Effects: mutates self

        __init__: Nat Float Float Bool -> None
        Requires: 0 <= num <= 9
                  0 <= x, y <= SCREEN_WIDTH - side
        '''
        self.num = num
        self.draft = 0
        self.x = x
        self.y = y
        self.fixed = fixed
        self.selected = False
        
    def draw(self, win):
        '''
        Draws the box on win

        Effects: may mutate win

        draw: Board Window -> None
        '''
        font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)

        if self.draft != 0 and self.num == 0:
            draft = font.render(str(self.draft), 1, DRAFT_COLOR)
            win.blit(draft, (self.x + DRAFT_SHIFT, self.y + DRAFT_SHIFT))
        elif self.num != 0:
            render_color = VALUE_COLOR
            if self.fixed:
                render_color = FIXED_COLOR
            num = font.render(str(self.num), 1, render_color)
            win.blit(num, (self.x + (self.side / 2 - num.get_width() / 2), 
                           self.y + (self.side / 2 - num.get_height() / 2)))

        if self.selected:
            pygame.draw.rect(win, SELECTED_COLOR, 
                             (self.x , self.y, self.side, self.side), 
                             BOX_BOARDER_WIDTH)

    def draw_num_only(self, win):
        '''
        Draws the box and its number only

        Effects: may mutate win

        draw: Board Window -> None
        '''
        font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)

        if self.num != 0:
            render_color = VALUE_COLOR
            if self.fixed:
                render_color = FIXED_COLOR
            num = font.render(str(self.num), 1, render_color)
            win.blit(num, (self.x + (self.side / 2 - num.get_width() / 2), 
                           self.y + (self.side / 2 - num.get_height() / 2)))

    
    def draw_solve(self, win, backtrack):
        '''
        Draw the box on win when drawing the solving process of the board

        Effects: mutates win

        draw_solve: Board Window Bool -> None
        '''
        font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)
        box_dim = (self.x, self.y, self.side, self.side)
        pygame.draw.rect(win, BG_COLOR, box_dim, 0)

        if self.num:
            num = font.render(str(self.num), 1, FIXED_COLOR)
            win.blit(num, (self.x + (self.side / 2 - num.get_width() / 2), 
                        self.y + (self.side / 2 - num.get_height() / 2)))
        if backtrack:
            pygame.draw.rect(win, SELECTED_COLOR, box_dim, BOX_BOARDER_WIDTH)
        else:
            pygame.draw.rect(win, PROGRESS_COLOR, box_dim, BOX_BOARDER_WIDTH)
        
                         
def get_time(secs):
    '''
    Returns a formatted time of secs

    get_time: Nat -> Str
    '''
    second = secs % 60
    minute = secs // 60
    return str(minute) + ":" + str(second)

def draw_window(win, bo, time, incorrect):
    '''
    Draws the sudoku board, bo, the play time and the number of incorrect 
        fillings on win

    Effects: mutates win
             print to pygame window

    draw_window: Window Board Nat Nat -> None
    '''
    win.fill(BG_COLOR)
    font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)

    text = font.render("Time: " + get_time(time), 1, TIME_COLOR)
    win.blit(text, TIME_POS)

    cross = font.render("X", 1, CROSS_COLOR)
    win.blit(cross, CROSS_POS)
    times = font.render(": " + str(incorrect), 1, INCRCT_COLOR)
    win.blit(times, INCRCT_POS)

    bo.draw(win)

    pygame.display.update()

def draw_game_result(win, time, incorrect):
    '''
    Draws the time it took to finished the game, the number of incorrect
        fillings and the follow up options on win

    Effects: mutates win
             print to pygame window

    draw_game_result: Window Nat Nat -> None
    '''
    win.fill(BG_COLOR)
    font = pygame.font.SysFont(SYSTEM_FONT, FONT_SIZE)

    time = font.render("Your time: " + get_time(time), 1, RESULT_COLOR)
    win.blit(time, (SCREEN_WIDTH / 2 - time.get_width() / 2, RESULT_TIME_Y))

    mistakes = font.render("Total mistakes: " + str(incorrect), 1, RESULT_COLOR)
    win.blit(mistakes, (SCREEN_WIDTH / 2 - mistakes.get_width() / 2, 
                         TOTAL_INCRT_Y))

    text = font.render("Press any key to start a new game", 1, RESULT_COLOR)
    win.blit(text, (SCREEN_WIDTH / 2 - text.get_width() / 2, MSG_Y))

    pygame.display.update()

def main():
    '''
    Creates a game of sudoku

    main: None -> None
    '''
    pygame.font.init()
    win = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Sudoku")

    game = True
    while game:
        bo = Board(SCREEN_WIDTH, SCREEN_WIDTH)
        bo.init_boxes()
        start = time.time()
        incorrect = 0

        solve_started = False
        rnd = True
        while rnd:
            play_time = round(time.time() - start)
            key = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    rnd = False
                    game = False

                if solve_started:
                    continue
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1 or event.key == pygame.K_KP1:
                        key = 1
                    elif event.key == pygame.K_2 or event.key == pygame.K_KP2:
                        key = 2
                    elif event.key == pygame.K_3 or event.key == pygame.K_KP3:
                        key = 3
                    elif event.key == pygame.K_4 or event.key == pygame.K_KP4:
                        key = 4
                    elif event.key == pygame.K_5 or event.key == pygame.K_KP5:
                        key = 5
                    elif event.key == pygame.K_6 or event.key == pygame.K_KP6:
                        key = 6
                    elif event.key == pygame.K_7 or event.key == pygame.K_KP7:
                        key = 7
                    elif event.key == pygame.K_8 or event.key == pygame.K_KP8:
                        key = 8
                    elif event.key == pygame.K_9 or event.key == pygame.K_KP9:
                        key = 9
                    elif event.key == pygame.K_DELETE or \
                         event.key == pygame.K_BACKSPACE:
                        bo.clear_draft()
                        key = None
                    elif event.key == pygame.K_SPACE:
                        solve_started = True
                        bo.redraw_select(win)
                        bo.visualize_solve(win)
                        key = None
                        rnd = False
                    elif event.key == pygame.K_RETURN:
                        set_result = bo.set_num()
                        if set_result == False:
                            incorrect += 1
                        elif set_result and bo.is_completed():
                            rnd = False
                        key = None

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    selected_box = bo.mouse_selection(mouse_pos)
                    if selected_box:
                        bo.select_box(selected_box[0], selected_box[1])
                        key = None
            
            if bo.box_selected and key:
                bo.set_draft(key)
                    
            draw_window(win, bo, play_time, incorrect)
        
        if game:
            pygame.time.delay(END_GAME_DELAY)
            draw_game_result(win, play_time, incorrect)
            
            another_one = True
            while another_one:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        game = False
                        another_one = False
                    elif event.type == pygame.KEYDOWN:
                        another_one = False

    pygame.quit()

if __name__ == '__main__':
    main()