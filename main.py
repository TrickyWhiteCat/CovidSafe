from multiprocessing import Process

from game import CovidGame
from solver import Solver


def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run(index:int = 0):
    board_path = f"board_{index}.out"
    cmd_path = f"command_{index}.inp"
    clear(board_path, cmd_path)

    solver = Solver(path_to_board=board_path, path_to_command=cmd_path)
    game = CovidGame(10, 10, board_filepath=board_path, command_filepath=cmd_path)

    play_game = Process(target = game.play)
    solve = Process(target = solver.solve)

    play_game.start()
    solve.start()
    while play_game.is_alive() or solve.is_alive():
        pass # Wait for both child process to finish

def work(num_trials, index=0):
    for trial in range(num_trials):
        run(index)


if __name__ == "__main__":
    clear("result.txt")
    NUM_CORES = 1
    num_trials = 10**4
    processes = []
    for core_idx in range(NUM_CORES):
        processes.append(Process(target=work, args=[num_trials, core_idx]))
        processes[-1].start()

    while sum([process.is_alive() for process in processes]):
        pass

    # Read all results
    with open("result.txt", 'r') as res_file:
        list_res = [int(val) for val in res_file.readlines()]
    
    print(f"Winrate: {sum(list_res)/len(list_res)}")