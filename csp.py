import random
from ortools.sat.python import cp_model

board_size = 16

class CSPSolution(cp_model.CpSolverSolutionCallback):
    def __init__(self,variables):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self.__variables = variables
        self.solution_list = [] # Solution List

    def on_solution_callback(self):
        sol = [self.Value(v) for v in self.__variables]
        #if sol not in self.solution_list:
        self.solution_list.append(sol)


def neighbors(board, row: int, col: int) -> dict:
        """Return neighbors of a cell given its position in the form of a dictionary whose keys = position and values = values of cells"""
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

      
model = cp_model.CpModel()
# A = [[' ' for i in range(board_size)] for j in range(board_size)]

A = [[ 0 , 0 , 0 , 0 , 1 ,' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [ 0 , 0 , 0 , 0 , 2 ,' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [ 0 , 0 , 0 , 0 , 2 ,' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [ 1 , 1 , 1 , 0 , 1 ,' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ', 3 , 2 , 2 ,' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' '],
     [' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ',' ']]


x = [[0 for i in range(board_size)] for j in range(board_size)]

# SetVariables
for row in range(board_size):
    for col in range(board_size):
        if A[row][col] == ' ':
            continue

        if A[row][col] == 'M':
            x[row][col] = 1
            continue

        neighbor_dict = neighbors(board=A, row=row, col=col)
        for pos in neighbor_dict:
            if neighbor_dict[pos] == " ":
                x[pos[0]][pos[1]] = model.NewIntVar(0,1,f'x[{pos[0]}][{pos[1]}]')


# SetConstraints
for row in range(board_size):
    for col in range(board_size):
        if A[row][col] == ' ' or A[row][col] == 0:
            continue

        if A[row][col] == 'M':
            x[row][col] = 1
            continue

        neighbor_dict = neighbors(board=x, row=row, col=col)

        model.AddAbsEquality(expr = sum(neighbor_dict.values()), target = A[row][col])

#All Solution
yy = []
for ii in range(board_size):
    for jj in range(board_size):
        if type(x[ii][jj]) != int:
            yy.append(x[ii][jj])
solver = cp_model.CpSolver()
solution_collector = CSPSolution(yy)
solver.SearchForAllSolutions(model, solution_collector)
print(solution_collector.solution_list)