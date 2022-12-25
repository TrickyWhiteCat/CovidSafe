from multiprocessing import Process

from game import CovidGame
from solver import Solver


def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run():
    clear("board.out", "command.inp")

    solver = Solver(path_to_board="board.out", path_to_command="command.inp")
    game = CovidGame(10, 10, board_filepath='board.out', command_filepath='command.inp')

    play_game = Process(target = game.play)
    solve = Process(target = solver.solve)

    play_game.start()
    solve.start()
    while play_game.is_alive() or solve.is_alive():
        pass # Wait for both child process to finish


if __name__ == "__main__":
    for trial in range(10**5):
        run()

    # Read all results
    with open("result.txt", 'r') as res_file:
        list_res = [int(val) for val in res_file.readlines()]
    
    print(f"Winrate: {sum(list_res/len(list_res))}")