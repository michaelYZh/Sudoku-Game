## This module provides functions that solve a sudoku board

## The following applies to all functions:
## Requires: bo is valid sudoku board (9x9 grid)

def find_empty(bo):
    '''
    Returns the position of the first empty element in bo

    find_empty: (listof (listof Nat)) -> (anyof (tupleof Nat Nat) None)

    Time: O(1) since there are always 81 elements in bo (9x9 sudoku board)
    '''
    for i in range(len(bo)):
        for j in range(len(bo[0])):
            if bo[i][j] == 0:
                return (i, j)

def valid(bo, num, pos):
    '''
    Determines if bo is a valid sudoku board or not when inserting num at pos

    valid: (listof (listof Nat)) Nat (tupleof Nat Nat) -> Bool
    Requires: pos is valid position in bo

    Time: O(1) since length of bo and length of elements of bo are always 9
    '''
    ## check row
    for i in range(len(bo[0])):
        if bo[pos[0]][i] == num and pos[1] != i:
            return False
    
    ## check column 
    for i in range(len(bo)):
        if bo[i][pos[1]] == num and pos[0] != i:
            return False

    box_cow = pos[1] // 3
    box_row = pos[0] // 3

    ## check the box containing pos
    for i in range(box_row * 3, box_row * 3 + 3):
        for j in range(box_cow * 3, box_cow * 3 + 3):
            if bo[i][j] == num and (i, j) != pos:
                return False

    return True

def solve(bo):
    '''
    Solves the sudoku board bo

    Effects: mutates bo

    solve: (listof (listof Nat)) -> Bool

    Time: O(1) since there are 9 options for a maximum of 81 unassigned numbers
    '''
    find = find_empty(bo)
    if not find:
        return True

    row, col = find
    for num in range(1, 10):
        if valid(bo, num, (row, col)):
            bo[row][col] = num
            if solve(bo):
                return True

    bo[row][col] = 0
    return False