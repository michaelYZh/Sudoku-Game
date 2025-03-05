# Sudoku Game

A modern, feature-rich Sudoku game with an optimized solver and clean Python implementation.

## Features

- 🎮 Clean and intuitive GUI
- 🎯 Multiple difficulty levels (Easy, Medium, Hard, Expert)
- ⚡ Optimized solver with backtracking, forward checking, and heuristics
- 📝 Draft mode for number candidates
- ⏱️ Timer and mistake counter
- 🎨 Modern UI with clear visual feedback
- ⌨️ Keyboard shortcuts for quick actions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/Sudoku-Game.git
cd Sudoku-Game
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the game:
```bash
python sudoku.py
```

### Controls

- **Mouse Click**: Select a cell
- **Number Keys (1-9)**: Add/remove draft numbers
- **Enter**: Place the selected draft number
- **Backspace**: Clear the selected cell
- **Space**: Auto-solve the puzzle

### Game Rules

1. Fill the 9x9 grid with numbers 1-9
2. Each row, column, and 3x3 box must contain all numbers 1-9 without repetition
3. Initial numbers cannot be changed
4. Use draft mode to mark potential numbers
5. Try to complete the puzzle with as few mistakes as possible

## Project Structure

- `sudoku.py`: Main game module with GUI implementation
- `solver.py`: Optimized Sudoku solver with multiple strategies
- `generate.py`: Puzzle generator with configurable difficulty
- `config.py`: Game configuration and constants

## Technical Details

The solver uses three optimization techniques:
1. Backtracking: Systematic search for solutions
2. Forward Checking: Early detection of invalid states
3. Heuristics: Smart cell and value selection

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
