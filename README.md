# Sudoku Solver

This is a program that can solve Sudokus for everyone too impatient for solving it by hand (like me).
It's supposed to solve all kinds of (solvable) Sudokus.
I haven't tested it, though, so it might not be able to solve specific combinations.

## Feeding a Sudoku

The Sudoku must be stored in a CSV file.

See examples for this in the `examples` directory.

## Running

Run the script like this:

    python3 solver.py sudoku_file1.csv sudoku_file2.csv ...

The script takes multiple Sudoku files as arguments.

It prints the name, the unfinished and the finished versions to the console.
