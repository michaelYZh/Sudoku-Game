# Sudoku-Game
## Instructions
1. Install all the packages from requirements.txt
2. Run sudoku.py and then have fun!!!

Here is a list of possible options:
  * Select the box you want to enter a number in. The box will have a red boarder if selected
  * Type in any number from the keyboard, and the number will be saved as a draft for the spot
  * Press 'Backspace' or 'Delete' to clear the draft in the box
  * If you are certain about your answer, press 'Enter'
    * If your answer is correct, the draft number is placed in the board
    * If not, the box is cleared, and the number of mistakes in the bottom left corner will increase by 1
  * You can press 'Space' to see the process of solving the board (do not press any key during the solving process)
  
## Adjustments
### sudoku.py
* SOLVE_PAUSE_TIME is how long each step of the solving process will show
  * The higher the longer

### generate.py
* SUDOKU_DIFFICULTY is the average rank of the board, you can see a more detailed explanation from
the documentation of [dukusan](https://pypi.org/project/dokusan/)
  * Basically, the higher the harder
  
## Other Notes
* Functions in solver.py can be used on sudoku boards in the form of a nested list, but they are not used in sudoku.py

## Credit
* I learned the structure of this game from a Youtube channel called [_Tech With Tim_](https://www.youtube.com/channel/UC4JX40jDee_tINbkjycV4Sg),
and I changed some of the implementation of the class and added the feature that allows user to play continuously and 
with a different board each time
