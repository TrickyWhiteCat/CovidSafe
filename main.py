from multiprocessing import Process

from game import CovidGame
from solver import Solver


def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run(index:int = 0, first_pos:tuple = None, result_path=None):
    board_path = f"board_{index}.out"
    cmd_path = f"command_{index}.inp"
    clear(board_path, cmd_path)

    solver = Solver(path_to_board=board_path, path_to_command=cmd_path, first_pos=first_pos, result_path=result_path)
    game = CovidGame(16, 40, board_filepath=board_path, command_filepath=cmd_path)

    play_game = Process(target = game.play)
    solve = Process(target = solver.solve)

    play_game.start()
    solve.start()
    while play_game.is_alive() and solve.is_alive():
        pass # Wait for child processes to finish

def work(num_trials, index=0, first_pos=None, result_path=None):
    for trial in range(num_trials):
        run(index, first_pos, result_path)


if __name__ == "__main__":

    NUM_CORES = 2
    

    row = 1
    col = 1

    res_path = f"result_{row}_{col}.txt"

    processes = [Process(target = work, args=[500, core_idx, (row, col), res_path]) for core_idx in range(NUM_CORES)]
    for process in processes:
        process.start()
    while sum([process.is_alive() for process in processes]):
        pas
    """
    while True:

        board_out = "board.out"
        cmd_inp = "cmd.inp"
        clear(board_out, cmd_inp)
        NUM_CORES = 1
        num_trials = 10**4

        game = CovidGame(9, 10, board_filepath=board_out, command_filepath=cmd_inp)
        solver = Solver(path_to_board=board_out, path_to_command=cmd_inp)

        game_process = Process(target=game.play)
        solver_process = Process(target=solver.solve)

        game_process.start()
        solver_process.start()

        while game_process.is_alive() and solver_process.is_alive():
            pass
    """
