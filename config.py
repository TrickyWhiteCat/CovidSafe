import util

board_path = f"board.out"
cmd_path = f"command.inp"

result_path = "csp.txt"

# Solver args
first_pos = None
wait = 0
use_least_square = True
use_cp_solver = False
timeout = 30

# Game args
board_size = 9
num_virus = 10