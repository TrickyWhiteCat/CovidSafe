import util
import config

import random
import time
import logging

import numpy as np

from ortools.sat.python import cp_model

log_path = "solver.log"
util.clear(log_path)
logging.basicConfig(filename=log_path, level=logging.INFO)
logger = logging.getLogger("solver")
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

        try: # Whether to solve as a linear system using least square method
            self.__use_least_square = kwargs["use_least_square"]
        except KeyError:
            self.__use_least_square = False

        try: # Whether to use cp_solver or not
            self.__use_cp_solver = kwargs["use_cp_solver"]
            if self.__use_cp_solver:
                self.__cp_solver = cp_model.CpSolver()
        except KeyError:
            self.__use_cp_solver = False

        try: # Set timeout for csp solver
            self.__csp_timeout = kwargs["csp_timeout"]
            self.__min_num_sol_cp_solver = kwargs["min_num_sol_cp_solver"]
        except KeyError:
            self.__csp_timeout = 30
            self.__min_num_sol_cp_solver = None

        try: # Wait for a few seconds before executing the next iteration
            self.__wait = kwargs["wait"]
        except KeyError:
            self.__wait = None

        logger.info(f"""Solver object was created with config:
                            board_path = {self.board_path}
                            command_path = {self.command_path}
                            result_path = {self.result_path}
                            first_pos = {self.__first_pos}
                            use_cp_solver = {self.__use_cp_solver}
                            first_pos = {self.__first_pos}
                            use_cp_solver = {self.__use_cp_solver}
                            timeout = {self.__csp_timeout}""")

        self.__iter = 0 # Used to sync between solver and game board
        self.solved = False # Whether the problem has been solved
        self.__finished = False # Finish flag
        self.__mark =  [] # A list containing positions of cells to be marked as bad cells
        self.__safe = [] # A list of  positions of cells that can be safely opened
        self.__border = [] # A list of positions of cells that are in the border. Go to __find_cells_in_border to read more.
        self.__undiscovered = [] # A list of positions of cells that aren't opened

    def __find_cells_in_border(self):
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
                        neighbors = self.__neighbors(row = row_idx, col = col_idx)
                        for neighbor_row, neighbor_col in neighbors:
                            if self.__board_state[neighbor_row][neighbor_col] == " ":
                                self.__border.append((row_idx, col_idx))
                                break
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
                        self.__virus_map = (np.array(board_state) == "M").astype(int).tolist() # We want to maintain the consistency use of list but numpy provide a convinient way to get the variable
                        return
                except ValueError:
                    pass

    def __write_all_possible(self):
        while self.__mark or self.__safe:
            self.__write_command()

    def __write_command(self, row = None, col = None, mark = None):

        if ((row is None) and (col is None) and (mark is None)):
            (row, col), mark = self.__choose_pos()

        if self.__wait:
            time.sleep(self.__wait)

        self.__read_board() # Called to wait for sync
        
        logger.info(f"Cell {(row, col)} was {'marked' if mark else 'revealed'}.")

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
                logger.info(f"New cell to mark from discovering {(cell_row, cell_col)}: {undiscovered}")
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
                logger.info(f"New safe to open cell after discovering {(cell_row, cell_col)}: {undiscovered}")
                self.__safe.extend(undiscovered)

    def __create_cp_variables(self):
        var = []
        var_pos = []
        model = cp_model.CpModel()
        for row, col in self.__border:
            cell_neighbor = self.__neighbors(row, col)

            # Making neighbors cells IntVar if they are unrevealed (have values == " ")
            for neighbor_row, neighbor_col in cell_neighbor:
                if self.__board_state[neighbor_row][neighbor_col] == " ":
                    if (neighbor_row, neighbor_col) in var_pos:
                        continue

                    int_var = model.NewIntVar(0, 1, name=f"{neighbor_row} {neighbor_col}")
                    logger.info(f"Cell {(neighbor_row, neighbor_col)} was added as a variable to the model.")
                    self.__virus_map[neighbor_row][neighbor_col] = int_var
                    var.append(int_var)
                    var_pos.append((neighbor_row, neighbor_col))
            
            # This dict containing pairs of key and value where the key is the position of a cell and the value is whether that cell contains virus
            neighbor_dict = util.neighbors(board=self.__virus_map, row=row, col=col) 
            model.Add(sum(neighbor_dict.values()) == int(self.__board_state[row][col]))
        
        # Total number of viruses found must be smaller than num_virus_left
        model.Add(sum(var) <= self.__num_virus_left)

        return model, var, var_pos

    def __create_linear_system_vars(self):
        var_pos = []
        target = []
        neighbor_dict = {}
        for row, col in self.__border:
            neighbor_dict[(row, col)] = self.__neighbors(row, col)
            cell_neighbor = neighbor_dict[(row, col)]

            count_surounding_virus = 0
            # Making neighbors cells IntVar if they are unrevealed (have values == " ")
            for neighbor_row, neighbor_col in cell_neighbor:
                if self.__virus_map[neighbor_row][neighbor_col]: # Cell contains virus
                    count_surounding_virus += 1
                    continue

                if self.__board_state[neighbor_row][neighbor_col] == " ":
                    if (neighbor_row, neighbor_col) in var_pos: # Cell was known and added to the list of var
                        continue
                    var_pos.append((neighbor_row, neighbor_col))

            target.append(int(self.__board_state[row][col]) - count_surounding_virus) # __board_state contains strings

        # Create parameter matrix
        param = np.zeros(shape=(len(target), len(var_pos)))

        for idx, (row, col) in enumerate(self.__border): # Since `param`'s rows correspond to a constraint assosiated with a cell in border, this for loop is equivalent to iterating through `param`'s rows
            for pos in neighbor_dict[(row, col)]:
                if pos in var_pos:
                    param[idx][var_pos.index(pos)] = 1
    
        return var_pos, param, target

    def __solve_with_least_square(self):
        logger.debug("Using least square")
        var, param, target = self.__create_linear_system_vars()
        # Solving param @ var = target. Since there can be many solutions, we use least square method.
        # The parts of `var` that unchange between solutions should have value around its true value (1 if contain virus and 0 otherwise)
        res = np.linalg.lstsq(param, target, rcond=None)[0]

        int_res = np.around(res)
        threshold = 10**-8
        flag = (np.abs(res - int_res) < threshold) # Result may be slightly off because of machine precision

        for idx, pos in enumerate(var):
            if flag[idx]:
                if int_res[idx] == 1:
                    self.__mark.append(pos)
                    logger.info(f"Cell {pos} is virus")
                if int_res[idx] == 0:
                    self.__safe.append(pos)
                    logger.info(f"Cell {pos} is safe")

        if not sum(flag):
            logger.warning(f"No context found using least square solver")

    def __choose_pos(self) -> tuple:
        """Return the position of cell to be chosen and whether we mark it as bad cell or not.
        Return: ((row, col), mark)"""
        if self.__mark: # Prioritize marking bad cells
            pos = self.__mark.pop(0)
            logger.info(f"Marking cell {pos}...")
            return pos, True

        if self.__safe:
            pos = self.__safe.pop(0)
            logger.info(f"Revealing cell {pos}...")
            return pos, False

        random_cell = random.choice(self.__undiscovered)
        logger.warning(f"Cell {random_cell} was randomly chosen.")
        return random_cell, False

    def __check_finished(self):
        has_V = False
        for row in self.__board_state:
            if "V" in row: # Virus detected
                has_V = True
                self.__finished = True

            if " " in row: # If we won (all cells are opened) then this case will never happen
                if has_V:
                    self.solved = False
                    logger.critical("Fail to solve the problem.")
                    return

        if has_V:
            self.solved = True
            logger.critical("Problem solved.")

    def __board_has_zero(self):
        for row in self.__board_state:
            for cell in row:
                if cell == "0":
                    return True
        return False

    def __solve_as_csp(self):
        # CpSolver is stateless, no need to create a new one in every function call.
        
        if self.__board_has_zero():
            pass
        else:
            logger.warning("Not enough context!")
            return "UNKNOWN"
        
        timeout = self.__csp_timeout
        if timeout:
            self.__cp_solver.parameters.max_time_in_seconds = self.__csp_timeout
            print(f"Trying to use CpSolver (time limit: {timeout}s)...")
        else:
            print(f"Trying to use CpSolver...")
        model, var, var_pos = self.__create_cp_variables()
        res = util.CSPSolution(variables=var, time_limit=self.__csp_timeout)
        logger.info("Preparing to use CpSolver...")
        status = self.__cp_solver.SearchForAllSolutions(model, res)
        logger.info(f"Found {len(res.solution_list)} solutions.")
        if len(res.solution_list) == 0:
            logger.warning("No solution found!")
            return status
        
        if res.timeout and self.__min_num_sol_cp_solver is not None and len(res.solution_list < self.__min_num_sol_cp_solver):
            logger.warning("Aborting...")
            return "TIMEOUT"

        first_row = res.solution_list[0]
        for case in res.solution_list:
            for idx, val in enumerate(first_row):
                if val != case[idx]: # If a cell contains 2 different values in 2 different cases then we cannot be sure about it
                    first_row[idx] = -1 # -1 acts as a flag to skip
        
        for idx, val in enumerate(first_row):
            if val == -1:
                continue

            pos = var_pos[idx]
            
            if val == 1 and pos not in self.__mark: # 1 means that cell contains a virus
                self.__mark.append(pos)
                logger.info(f"Cell {pos} with {val=} was determined as containing virus from CpSolver")

            elif val == 0 and pos not in self.__safe:
                self.__safe.append(pos)
                logger.info(f"Cell {pos} with {val=} was determined as safe to reveal from CpSolver")
        
        return status

    def solve(self):
        self.__iter = 0

        # First iteration
        if isinstance(self.__first_pos, tuple) and (None not in self.__first_pos):
            self.__write_command(row=self.__first_pos[0], col=self.__first_pos[1], mark=False)

        while not self.__finished:
            logger.info(f"Iteration {self.__iter} started")

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
                continue # Codes below are used if we cannot use logic

            if self.__border and self.__use_least_square:
                self.__solve_with_least_square()

                if self.__safe or self.__mark:
                    while self.__mark or self.__safe:
                        self.__write_command()
                    continue # Codes below are used if we cannot use least square
                
            if self.__border and self.__use_cp_solver:
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
        
        if self.result_path is not None:
            with open(self.result_path, 'a') as res_file:
                res_file.write(f"{int(self.solved)}\n")

def main():
    solver = Solver(path_to_board=config.board_path,
                    path_to_command=config.cmd_path,
                    first_pos=config.first_pos,
                    result_path=config.result_path,
                    use_least_square = config.use_least_square,
                    use_cp_solver = config.use_cp_solver,
                    csp_timeout = config.timeout,
                    min_num_sol_cp_solver = config.min_num_sol_cp_solver,
                    wait=config.wait)

    solver.solve()

if __name__ == "__main__":
    main()