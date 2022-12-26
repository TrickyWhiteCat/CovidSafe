import random
import time


class Solver:
    def __init__(self, path_to_board: str = None, path_to_command: str = None):
        """
        `path_to_board`: path to the csv file containing data from the board.
        `path_to_command`: path to the csv file containing command (output from the solver)"""
        if path_to_board is None:
            path_to_board = "board.out"
        self.board_path = path_to_board
        
        if path_to_command is None:
            path_to_command = "command.inp"
        self.command_path = path_to_command

        self.__iter = 1
        self.solved = False
        self.__finished = False
        self.__safe = []
        self.__border = []
        self.__undiscovered = []

    def __find_cells_in_border(self) -> list:
        """Return a list of positions of cells that are discovered and containing positive numbers whose neighbors aren't fully discovered.
        Example:
        |  |  | 1|
        |  | 3| V|
        |  | V| 2|
        -> Cells containing 3 and 1 are returned
        """

        for row_idx, row in enumerate(self.__board_state):
            for col_idx, cell in enumerate(row):
                try:
                    if (row_idx, col_idx) in self.__border:
                        continue # Skip if existed
                    if int(cell) > 0: # Will throw a ValueError if that cell contains "V" or " " and the condition will be Falsed if the cell's value is 0
                        self.__border.append((row_idx, col_idx))
                except ValueError:
                    pass  

    def __neighbors(self, row: int, col: int) -> dict:
        """Return neighbors of a cell given its position in the form of a dictionary whose keys = position and values = values of cells"""
        if row >= len(self.__board_state) or col >= len(self.__board_state[0]):
            raise ValueError(f"Position ({row}, {col}) is out of the board.")
        
        neighbor = {} 
        for neighbor_row in range(row - 1, row + 2): # in [row - 1, row + 1]
            for neighbor_col in range(col - 1, col + 2):
                try: # Avoid index out of range for cells in the border
                    neighbor[(neighbor_row, neighbor_col)] = self.__board_state[neighbor_row][neighbor_col]
                except IndexError:
                    pass
        return neighbor

    def __read_board(self):
        path = self.board_path
        while True: # Wait for the file to be updated
            with open(path, mode='r') as board:
                try:
                    iter = int(board.readline())
                    if iter < self.__iter:
                        lines = board.readlines()
                        board_state = []

                        for row_idx, line in enumerate(lines):
                            cells_list = line.split(",")
                            board_state.append(cells_list)

                            for col_idx, cell in enumerate(line.split(",")):
                                if cell == " ":
                                    self.__undiscovered.append((row_idx, col_idx))
                                    
                        self.__board_state = board_state
                        return
                except ValueError:
                    pass

    def __write_command(self, row, col, mark: bool = False):
        content = f"{row} {col} M" if mark else f"{row} {col}"
        with open(self.command_path, mode = 'w') as cmd:
            cmd.write(f"{self.__iter}\n")
            cmd.write(content)
            self.__iter += 1
            cmd.close()

    def __find_safe_cells(self):
        
        self.__find_cells_in_border()
        
        while self.__border:

            cell_row, cell_col = self.__border.pop() # Get a cell and remove it from the list
            cell_value = int(self.__board_state[cell_row][cell_col])
            
            neighbors = self.__neighbors(row = cell_row, col = cell_col)
            undiscovered = []
            count_bad = 0

            for pos in neighbors:
            
                if pos in self.__safe: # Skip existed
                    continue

                value = neighbors[pos]
                if value == "V":
                    count_bad += 1
                    continue
                if value == " ":
                    undiscovered.append(pos)
            
            if count_bad == cell_value: # Our cell has already contact enough bad cells. Other undiscovered cells are safe to open
                self.__safe.extend(undiscovered)


    def __choose_pos(self) -> tuple:
        if self.__safe:
            return self.__safe.pop()

        return [val + 1 for val in random.choice(self.__undiscovered)]    

    def __check_finished(self):
        for row in self.__board_state:
            if "V" in row: # Virus detected
                self.solved = False
                self.__finished = True
                return
        
        for row in self.__board_state:
            if " " in row: # There exists unopened cell
                self.__finished = False
                return

        # No unopened cell left
        self.__finished = True
        self.solved = True


    def solve(self):
        while not self.__finished:
            time.sleep(1)
            self.__read_board()

            if not self.__safe: # If there isn't any safe to open cell left, we need to find new one.
                self.__find_safe_cells()

            row, col = self.__choose_pos()
            self.__write_command(row = row, col = col)
            self.__check_finished()
        
        with open("result.txt", 'a') as res_file:
            res_file.write(f"{int(self.solved)}\n")