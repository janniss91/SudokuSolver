import argparse
import csv

from collections import Counter
from copy import deepcopy
from typing import List
from typing import Tuple
from typing import Union

NUMBERS = [str(number) for number in range(10)]


class SudokuTable:
    def __init__(self, file_name: str):
        self.rows = []
        self.columns = [[] for _ in range(9)]
        self.squares = [[] for _ in range(9)]

        # Initialize a dictionary for mapping coordinates to their respective
        # squares.
        self.coordinate_to_square = {}

        # Initialize a dictionary for storing the true numbers found in a square.
        self.square_to_numbers = {
            0: [],
            1: [],
            2: [],
            3: [],
            4: [],
            5: [],
            6: [],
            7: [],
            8: [],
        }

        # Set up a dictionary mapping squares to all their coordinates.
        self.square_to_coordinates = deepcopy(self.square_to_numbers)

        # Initialize dictionaries for storing the true numbers found in rows and
        # columns. Deep copies of the dictionary above are used for convenience.
        self.row_to_numbers = deepcopy(self.square_to_numbers)
        self.column_to_numbers = deepcopy(self.square_to_numbers)

        # Read a Sudoku from a file.
        self._read_sudoku_from_file(file_name)

    def _read_sudoku_from_file(self, filename: str):
        with open(filename, "r") as sudoku_file:
            csv_reader = csv.reader(sudoku_file, delimiter=",")
            for row_number, row in enumerate(csv_reader):
                row = [int(entry) if entry in NUMBERS else entry for entry in row]
                self._fill_row(row, row_number)
                self._fill_columns(row)
                self._fill_squares(row, row_number)

            if len(self.rows) != 9 and not all([len(row) == 9 for row in self.rows]):
                raise Exception("The Sudoku table is invalid.")

    def _fill_row(self, row: List[str], row_number: int):
        self.rows.append(row)
        for entry in row:
            if type(entry) == int:
                self.row_to_numbers[row_number].append(entry)

    def _fill_columns(self, row: List[List[str]]):
        for column_number, entry in enumerate(row):
            self.columns[column_number].append(entry)
            if type(entry) == int:
                self.column_to_numbers[column_number].append(entry)

    def _fill_squares(self, row: List[Union[str, int]], row_number: int):
        """
        This method could be refactored.
        :param row:
        :param row_number:
        :return:
        """
        if 0 <= row_number < 3:
            start = 0
            end = 3
            for square_num in range(3):
                self.squares[square_num].append(row[start:end])
                for index in range(start, end):
                    self.coordinate_to_square[(row_number, index)] = square_num
                    self.square_to_coordinates[square_num].append((row_number, index))
                    if type(row[index]) == int:
                        self.square_to_numbers[square_num].append(row[index])
                start = end
                end += 3
        elif 3 <= row_number < 6:
            start = 0
            end = 3
            for square_num in range(3, 6):
                self.squares[square_num].append(row[start:end])
                for index in range(start, end):
                    self.coordinate_to_square[(row_number, index)] = square_num
                    self.square_to_coordinates[square_num].append((row_number, index))
                    if type(row[index]) == int:
                        self.square_to_numbers[square_num].append(row[index])
                start = end
                end += 3
        else:
            start = 0
            end = 3
            for square_num in range(6, 9):
                self.squares[square_num].append(row[start:end])
                for index in range(start, end):
                    self.coordinate_to_square[(row_number, index)] = square_num
                    self.square_to_coordinates[square_num].append((row_number, index))
                    if type(row[index]) == int:
                        self.square_to_numbers[square_num].append(row[index])
                start = end
                end += 3

    def set_field(self, row: int, column: int, value: int):
        self.rows[row][column] = value
        self.columns[column][row] = value

    def get_field(self, row: int, column: int) -> int:
        return self.rows[row][column]

    def print_table(self):
        for row in self.rows:
            for entry in row:
                print(entry, end=" ")
            print()


class SudokuSolver:
    def __init__(self, table: SudokuTable):
        self.table = table

        self.possible = {}
        self._initialise_possible()

    def _initialise_possible(self):
        for row, column in self.table.coordinate_to_square:
            if isinstance(self.table.rows[row][column], str):
                self.possible[(row, column)] = [1, 2, 3, 4, 5, 6, 7, 8, 9]
            else:
                self.possible[(row, column)] = self.table.rows[row][column]

    def solve(self):
        iter_count = 0
        while (
            any([type(possible) != int for possible in self.possible.values()])
            and iter_count < 9
        ):
            # Use easy_solve until self.possible is not changed by it anymore.
            possible_copy = None
            while possible_copy != self.possible:
                possible_copy = self.possible
                self.easy_solve()

            possible_copy = None
            while possible_copy != self.possible:
                possible_copy = self.possible
                self.check_two_item_coordinate_per_square()

            possible_copy = None
            while possible_copy != self.possible:
                possible_copy = self.possible
                self.check_single_elements_in_column()
                self.check_single_elements_in_row()

            iter_count += 1

        self.check_table_validity()

        if any([type(possible) != int for index, possible in self.possible.items()]):
            self.print_resulting_table()
            print("This Sudoku cannot be solved by this program.")
        else:
            self.print_resulting_table()

    def easy_solve(self):
        """
        Check the output of the easy sudoku to see whether this really works.
        :return:
        """
        for row_number in range(len(self.table.rows)):
            for column_number in range(len(self.table.columns)):
                coordinate = (row_number, column_number)
                if type(self.possible[coordinate]) == list:
                    self.check_row_easy_solve(coordinate)
                if type(self.possible[coordinate]) == list:
                    self.check_column_easy_solve(coordinate)
                if type(self.possible[coordinate]) == list:
                    self.check_square_easy_solve(coordinate)

    def check_row_easy_solve(self, coordinate: Tuple[int, int]):
        for true_number in self.table.row_to_numbers[coordinate[0]]:
            if true_number in self.possible[coordinate]:
                self.possible[coordinate].remove(true_number)

        if len(self.possible[coordinate]) == 1:
            new_true = self.possible[coordinate][0]
            self.table.column_to_numbers[coordinate[1]].append(new_true)
            self.table.square_to_numbers[
                self.table.coordinate_to_square[coordinate]
            ].append(new_true)

            if new_true not in self.table.row_to_numbers[coordinate[0]]:
                self.table.row_to_numbers[coordinate[0]].append(new_true)

            self.possible[coordinate] = new_true
            self.table.set_field(coordinate[0], coordinate[1], new_true)

    def check_column_easy_solve(self, coordinate: Tuple[int, int]):
        for true_number in self.table.column_to_numbers[coordinate[1]]:
            if true_number in self.possible[coordinate]:
                self.possible[coordinate].remove(true_number)

        if len(self.possible[coordinate]) == 1:
            new_true = self.possible[coordinate][0]
            self.table.row_to_numbers[coordinate[0]].append(new_true)
            self.table.square_to_numbers[
                self.table.coordinate_to_square[coordinate]
            ].append(new_true)

            if new_true not in self.table.column_to_numbers[coordinate[1]]:
                self.table.column_to_numbers[coordinate[1]].append(new_true)

            self.possible[coordinate] = new_true
            self.table.set_field(coordinate[0], coordinate[1], new_true)

    def check_square_easy_solve(self, coordinate: Tuple[int, int]):
        relevant_square = self.table.coordinate_to_square[coordinate]

        for true_number in self.table.square_to_numbers[relevant_square]:
            if true_number in self.possible[coordinate]:
                self.possible[coordinate].remove(true_number)

        if len(self.possible[coordinate]) == 1:
            new_true = self.possible[coordinate][0]
            self.table.row_to_numbers[coordinate[0]].append(new_true)
            self.table.column_to_numbers[coordinate[1]].append(new_true)

            if (
                new_true
                not in self.table.square_to_numbers[
                    self.table.coordinate_to_square[coordinate]
                ]
            ):
                self.table.square_to_numbers[
                    self.table.coordinate_to_square[coordinate]
                ].append(new_true)

            self.possible[coordinate] = new_true
            self.table.set_field(coordinate[0], coordinate[1], new_true)

    def check_two_item_coordinate_per_square(self):
        """
        Seemed to work at first sight but check again!
        :return:
        """
        # Iterate over all 9 squares.
        for square, coordinates in self.table.square_to_coordinates.items():
            # Make a list of all values with 2 possible numbers.
            two_numbers = [
                tuple(self.possible[coordinate])
                for coordinate in coordinates
                if isinstance(self.possible[coordinate], list)
                and len(self.possible[coordinate]) == 2
            ]
            # Set up a set with equal values from the list with 2 possible numbers.
            entry_counter = Counter(two_numbers)
            equal_entries = set(
                [entry for entry in two_numbers if entry_counter[entry] > 1]
            )

            # Don't bother getting into the for loop if no equal entries of
            # length 2 exist.
            if equal_entries:
                for coordinate in coordinates:
                    for equal_entry in equal_entries:
                        for number in equal_entry:
                            if (
                                isinstance(self.possible[coordinate], list)
                                and list(equal_entry) != self.possible[coordinate]
                                and number in self.possible[coordinate]
                            ):
                                self.possible[coordinate].remove(number)

                    if (
                        isinstance(self.possible[coordinate], list)
                        and len(self.possible[coordinate]) == 1
                    ):
                        new_true = self.possible[coordinate][0]
                        self.table.row_to_numbers[coordinate[0]].append(new_true)
                        self.table.column_to_numbers[coordinate[1]].append(new_true)

                        if (
                            new_true
                            not in self.table.square_to_numbers[
                                self.table.coordinate_to_square[coordinate]
                            ]
                        ):
                            self.table.square_to_numbers[
                                self.table.coordinate_to_square[coordinate]
                            ].append(new_true)

                        self.possible[coordinate] = new_true
                        self.table.set_field(coordinate[0], coordinate[1],
                                             new_true)

    def check_single_elements_in_column(self):
        """
        Checks for numbers that are only possible in one cell of a column and
        sets this cell to this number.
        """
        possible_columns = []
        for column in range(len(self.table.columns)):
            possible_columns.append([])
            for row in range(len(self.table.rows)):
                values = self.possible[(row, column)]
                possible_columns[column].append(values if isinstance(values, list) else [values])

        for column, poss_col in enumerate(possible_columns):
            for row, possible in enumerate(poss_col):
                for number in possible:
                    if not any([number in poss for count, poss in enumerate(poss_col) if count != row]):
                        self.table.row_to_numbers[row].append(number)
                        self.table.square_to_numbers[
                            self.table.coordinate_to_square[(row, column)]
                        ].append(number)

                        if number not in self.table.column_to_numbers[column]:
                            self.table.column_to_numbers[column].append(number)

                        self.possible[(row, column)] = number
                        self.table.set_field(row, column, number)

    def check_single_elements_in_row(self):
        """
        Checks for numbers that are only possible in one cell of a row and
        sets this cell to this number.
        """
        possible_rows = []
        for row in range(len(self.table.rows)):
            possible_rows.append([])
            for col in range(len(self.table.columns)):
                values = self.possible[(row, col)]
                possible_rows[row].append(values if isinstance(values, list) else [values])

        for row, poss_row in enumerate(possible_rows):
            for col, possible in enumerate(poss_row):
                for number in possible:
                    if not any([number in poss for count, poss in enumerate(poss_row) if count != col]):
                        self.table.column_to_numbers[col].append(number)
                        self.table.square_to_numbers[
                            self.table.coordinate_to_square[(row, col)]
                        ].append(number)

                        if number not in self.table.column_to_numbers[col]:
                            self.table.row_to_numbers[row].append(number)

                        self.possible[(row, col)] = number
                        self.table.set_field(row, col, number)

    def check_table_validity(self):
        """
        Checks whether a resulting table is a valid Sudoku table.
        :return:
        """
        for row in self.table.rows:
            if len(row) != 9 or set(row) != {1,2,3,4,5,6,7,8,9}:
                print(row)
                raise Exception("The sudoku table is not valid. Improve your "
                                "algorithm. Check rows of table.")
        for col in self.table.columns:
            if len(col) != 9 or set(col) != {1,2,3,4,5,6,7,8,9}:
                print(col)
                raise Exception("The sudoku table is not valid. Improve your "
                                "algorithm. Check columns of table.")

        count_results = Counter(self.possible.values())
        for count in list(count_results.values()):
            if count != 9:
                raise Exception("The sudoku table is not valid. Improve your "
                                "algorithm. Check possible dictionary.")

    def print_resulting_table(self):
        line_count = 0
        square_count = 0
        for coord, value in self.possible.items():
            print("{}".format(str(value)), end=" ")
            line_count += 1
            square_count += 1
            if square_count > 2:
                print(" ", end="")
                square_count = 0
            if line_count > 8:
                print()
                line_count = 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("sudoku_file", nargs="+")

    args = parser.parse_args()

    for sudoku_file in args.sudoku_file:
        table = SudokuTable(sudoku_file)

        print(sudoku_file)
        print()
        table.print_table()
        print()

        solver = SudokuSolver(table)

        solver.solve()
        print()
