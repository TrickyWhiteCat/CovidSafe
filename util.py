import time
import logging

from ortools.sat.python import cp_model



def neighbors(board, row: int, col: int) -> dict:
        """An other version of neighbors which allows passing custom board"""
        if row >= len(board) or col >= len(board[0]):
            raise ValueError(f"Position ({row}, {col}) is out of the board.")
        
        neighbor = {} 
        for neighbor_row in range(row - 1, row + 2): # in [row - 1, row + 1]
            for neighbor_col in range(col - 1, col + 2):
                if neighbor_col < 0 or neighbor_row < 0:
                    continue
                if neighbor_row == row and neighbor_col == col:
                    continue
                try: # Avoid index out of range for cells in the border
                    neighbor[(neighbor_row, neighbor_col)] = board[neighbor_row][neighbor_col]
                except IndexError:
                    pass
        return neighbor

def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

class CSPSolution(cp_model.CpSolverSolutionCallback):
    def __init__(self,variables, time_limit = None):
        self.__logger = logging.getLogger(name="solver")
        self.__time_limit = time_limit
        self.__start_time = time.time()
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solution_list = [] # Solution List
        self.timeout = False

    def on_solution_callback(self):
        if self.__time_limit:
            if time.time() - self.__start_time > self.__time_limit:
                if self.__logger:
                    self.__logger.warning(f"Time limit exceeded. Got {len(self.solution_list)} solutions so far.")
                self.timeout = True
                self.StopSearch()
        sol = [self.Value(v) for v in self.__variables]
        if sol not in self.solution_list:
            self.solution_list.append(sol)