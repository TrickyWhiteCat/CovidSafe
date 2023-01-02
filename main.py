from multiprocessing import Process

from game import CovidGame
from solver import Solver


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
    
    NUM_CORES = 2

    for row in range(15, 0, -1):
        for col in range(15, 0, -1):
            result_path = f"{row}_{col}.txt"

            processes = [Process(target = run, args=[core_idx, 500, (row, col), result_path]) for core_idx in range(NUM_CORES)]
            for process in processes:
                process.start()

            while sum([process.is_alive() for process in processes]):
                pass