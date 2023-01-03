import util
import config

import random
import time
import logging

import numpy as np

from ortools.sat.python import cp_model

logging.basicConfig(format=logging.BASIC_FORMAT,
                    filename="solver.log")
class Solver:
    def __init__(self, path_to_board: str = None, path_to_command: str = None, **kwargs):
        """
        `path_to_board`: path to the file containing data from the board.
        `path_to_command`: path to the file containing command (output from the solver)"""
        if path_to_board is None:
            path_to_board = "board.out"
        self.board_path = path_to_board
        
        if path_to_command is None:
            path_to_command = "command.inp"
        self.command_path = path_to_command

        try: # The file that the result will be written to. Useful when the game is run more than 1 time
            self.result_path = kwargs["result_path"]
        except KeyError:
            self.result_path = None

        try:
            self.__first_pos = kwargs["first_pos"]
        except KeyError:
            self.__first_pos = None

        try: # Try to get CSP Model and Solver
            self.__cp_model = kwargs["cp_model"]
            self.__cp_solver = kwargs["cp_solver"]
        except KeyError:
            self.__cp_model = None
            self.__cp_solver = None

        try: # Set timeout for csp solver
            self.__csp_timeout = kwargs["csp_timeout"]
        except KeyError:
            self.__csp_timeout = 60

        try: # Wait for a few seconds before executing the next iteration
            self.__wait = kwargs["wait"]
        except KeyError:
            self.__wait = None

        logging.info(f"""Solver object was created with config:
                            board_path = {self.board_path}
                            command_path = {self.command_path}
                            result_path = {self.result_path}
                            cp_model = {self.__cp_model}
                            cp_solver = {self.__cp_solver}
                            timeout = {self.__csp_timeout}""")

        self.__iter = 0 # Used to sync between solver and game board
        self.solved = False # Whether the problem has been solved
        self.__finished = False # Finish flag
        self.__mark =  [] # A list containing positions of cells to be marked as bad cells
        self.__safe = [] # A list of  positions of cells that can be safely opened
        self.__border = [] # A list of positions of cells that are in the border. Go to __find_cells_in_border to read more.
        self.__undiscovered = [] # A list of positions of cells that aren't opened

    def __find_cells_in_border(self) -> list:
        """Return a list of positions of cells that are discovered and containing positive numbers whose neighbors aren't fully discovered.
        
        Example:

        | _| _| 1|\n
        | _| 3| V|\n
        | _| V| 2|\n

        -> A list which consists of cells containing positions of 3 and 1 are returned
        """
        self.__border = [] # Reset

        for row_idx, row in enumerate(self.__board_state):
            for col_idx, cell in enumerate(row):
                try:
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
                if neighbor_col < 0 or neighbor_row < 0:
                    continue
                if neighbor_row == row and neighbor_col == col:
                    continue
                try: # Avoid index out of range for cells in the border
                    neighbor[(neighbor_row, neighbor_col)] = self.__board_state[neighbor_row][neighbor_col]
                except IndexError:
                    pass
        return neighbor

    def __read_board(self):
        """Read the current board state."""
        path = self.board_path
        self.__undiscovered = []
        while True: # Wait for the file to be updated
            with open(path, mode='r') as board:
                try:
                    iter, self.__num_virus_left = [int(val) for val in board.readline().split()]
                    if iter == self.__iter:
                        lines = board.readlines()
                        board_state = []

                        for row_idx, line in enumerate(lines):
                            line = line.replace("\n", "") # Remove \n characters
                            cells_list = line.split(",")
                            board_state.append(cells_list)

                            for col_idx, cell in enumerate(line.split(",")):
                                if cell == " ":
                                    self.__undiscovered.append((row_idx, col_idx))
                                    
                        self.__board_state = board_state
                        self.__virus_map = (np.array(board_state) == "M").astype(int).tolist() # We want to maintain the consistent use of list but numpy provide a convinient way to get the variable
                        return
                except ValueError:
                    pass

    def __write_command(self, row = None, col = None, mark = None):

        if ((row is None) and (col is None) and (mark is None)):
            (row, col), mark = self.__choose_pos()

        if self.__wait:
            time.sleep(self.__wait)

        self.__read_board() # Called to wait for sync

        content = f"{row + 1} {col + 1} M" if mark else f"{row + 1} {col + 1}" # Board are indexed from 1 instead of 0
        with open(self.command_path, mode = 'w') as cmd:
            self.__iter += 1
            cmd.write(f"{self.__iter}\n")
            cmd.write(content)
            cmd.close()

    def __find_bad_cells(self):
        """Bad cells are cells containing virus. We can find bad cells by examining border cell whose number of undiscovered neighbors equals to its value."""
        
        for cell_row, cell_col in self.__border:

            cell_value = int(self.__board_state[cell_row][cell_col])

            neighbors = self.__neighbors(row = cell_row, col = cell_col)
            undiscovered = []
            count_undiscovered = 0

            for pos in neighbors:

                value = neighbors[pos]
                if value == "M":
                    count_undiscovered += 1
                    continue

                if value == " ":
                    count_undiscovered += 1
                    if pos not in self.__mark:
                        undiscovered.append(pos)
            
            if count_undiscovered == cell_value:
                self.__mark.extend(undiscovered)

    def __find_safe_cells(self):
        
        for cell_row, cell_col in self.__border:

            cell_value = int(self.__board_state[cell_row][cell_col])
            
            neighbors = self.__neighbors(row = cell_row, col = cell_col)
            undiscovered = []
            count_bad = 0

            for pos in neighbors:
            
                if pos in self.__safe: # Skip existed
                    continue

                value = neighbors[pos]
                if value == "M" or pos in self.__mark:
                    count_bad += 1
                    continue
                if value == " ":
                    undiscovered.append(pos)
            
            if count_bad == cell_value: # Our cell has already contact enough bad cells. Other undiscovered cells are safe to open
                self.__safe.extend(undiscovered)


    def __create_csp_variables(self):
        var = []
        var_pos = []
        for row, col in self.__border:
            cell_neighbor = self.__neighbors(row, col)

            # Making neighbors cells IntVar if they are unrevealed (have values == " ")
            for neighbor_row, neighbor_col in cell_neighbor:
                if self.__board_state[neighbor_row][neighbor_col] == " ":
                    if (neighbor_row, neighbor_col) in var_pos:
                        continue
                    var_pos.append((neighbor_row, neighbor_col))

                    int_var = self.__cp_model.NewIntVar(0, 1, name=f"{neighbor_row} {neighbor_col}")
                    self.__virus_map[neighbor_row][neighbor_col] = int_var
                    var.append(int_var)
            
            # This dict containing pairs of key and value where the key is the position of a cell and the value is whether that cell contains virus
            neighbor_dict = util.neighbors(board=self.__virus_map, row=row, col=col) 
            self.__cp_model.Add(sum(neighbor_dict.values()) == int(self.__board_state[row][col]))
        
        # Total number of viruses found must be smaller than num_virus_left
        self.__cp_model.Add(sum(var) <= self.__num_virus_left)

        return var, var_pos


    def __choose_pos(self) -> tuple:
        """Return the position of cell to be chosen and whether we mark it as bad cell or not.
        Return: ((row, col), mark)"""
        if self.__mark: # Prioritize marking bad cells
            pos = self.__mark.pop(0)
            return pos, True

        if self.__safe:
            pos = self.__safe.pop(0)
            return pos, False

        return random.choice(self.__undiscovered), False

    def __check_finished(self):
        has_V = False
        for row in self.__board_state:
            if "V" in row: # Virus detected
                has_V = True
                self.__finished = True

            if " " in row: # If we won (all cells are opened) then this case will never happen
                if has_V:
                    self.solved = False
                    return

        if has_V:
            self.solved = True

    def __solve_as_csp(self):
        if self.__cp_model is None or self.__cp_solver is None:
            return
        
        timeout = self.__csp_timeout
        if timeout:
            self.__cp_solver.parameters.max_time_in_seconds = self.__csp_timeout
            print(f"Trying to use CSP (timeout duration: {timeout}s)...")
        else:
            print(f"Trying to use CSP")
        var, var_pos = self.__create_csp_variables()
        res = util.CSPSolution(variables=var)
        self.__cp_solver.SearchForAllSolutions(self.__cp_model, res)
        if len(res.solution_list) == 0:
            return

        first_row = res.solution_list[0]
        for case in res.solution_list:
            for idx, val in enumerate(first_row):
                if val != case[idx]: # If a cell contains 2 different values in 2 different cases then we cannot be sure about it
                    first_row[idx] = -1 # -1 acts as a flag to skip
        
        for idx, val in enumerate(first_row):
            if val == -1:
                continue

            pos = var_pos[idx]
            
            if val == 1: # 1 means that cell contains a virus
                self.__mark.append(pos)

            if val == 0:
                self.__safe.append(pos)

        return


    def solve(self):
        self.__iter = 0

        # First iteration
        if isinstance(self.__first_pos, tuple) and (None not in self.__first_pos):
            self.__write_command(row=self.__first_pos[0], col=self.__first_pos[1], mark=False)

        while not self.__finished:

            self.__read_board()
            
            self.__check_finished()
            if self.__finished:
                break
            
            self.__find_cells_in_border()
            
            self.__find_bad_cells()
            self.__find_safe_cells()
            
            if self.__safe or self.__mark:
                while self.__mark or self.__safe:
                    self.__write_command()
                continue # Codes below are used to choose a random cell to open, which is redundant if we flagged or opened a cell in current iteration
                
            if self.__border:
                self.__solve_as_csp()

            if self.__safe or self.__mark:
                while self.__mark or self.__safe:
                    self.__write_command()
                continue # Codes below are used to choose a random cell to open, which is redundant if we flagged or opened a cell in current iteration

            self.__check_finished()
            if self.__finished:
                break

            # A random cell
            self.__write_command()
        
        #if self.__iter != 2: # Skip lost from the beginning
        with open(self.result_path, 'a') as res_file:
            res_file.write(f"{int(self.solved)}\n")

def main():

    solver = Solver(path_to_board="board.out",
                    path_to_command="command.inp",
                    first_pos=config.first_pos,
                    result_path=config.result_path,
                    cp_model = cp_model.CpModel(),
                    cp_solver = cp_model.CpSolver(),
                    wait=config.wait)

    solver.solve()

if __name__ == "__main__":
    main()