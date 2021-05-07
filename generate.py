## This module provides function that generates a sudoku board

from dokusan import generators, stats
from solver import solve
import numpy as np

SUDOKU_DIFFICULTY = 100 # The higher the harder

def generate_board():
    '''
    Returns a sudoku board with all empty slots being 0

    generate_board: None -> (listof (listof Nat))
    '''
    while True:
        bo = generators.random_sudoku(avg_rank = SUDOKU_DIFFICULTY)
        if stats.rank(sudoku := bo) < SUDOKU_DIFFICULTY:
            break
    los = list(str(bo))
    lon = [int(str) for str in los]
    board = np.array(lon).reshape(9, 9)
    return board