from game import CovidGame
from solver import Solver

from multiprocessing import Process

def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run(index:int = 0, num_trials=1000, first_pos=None, result_path=None):
    for trial in range(num_trials):
        board_path = f"board_{index}.out"
        cmd_path = f"command_{index}.inp"
        clear(board_path, cmd_path)

        solver = Solver(path_to_board=board_path, path_to_command=cmd_path, first_pos=first_pos, result_path=result_path)
        game = CovidGame(9, 10, board_filepath=board_path, command_filepath=cmd_path)

        play_game = Process(target = game.play)
        solve = Process(target = solver.solve)

        play_game.start()
        solve.start()
        while play_game.is_alive() and solve.is_alive():
            pass # Wait for both child process to finish

if __name__ == "__main__":
    
    result_path = f"csp_test.txt"
    board_path = f"board.out"
    cmd_path = f"command.inp"
    clear(board_path, cmd_path)
    game = CovidGame(11, 10, board_filepath=board_path, command_filepath=cmd_path)
    game.play()