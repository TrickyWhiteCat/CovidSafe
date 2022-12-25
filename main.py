from multiprocessing import Process

from game import CovidGame
from solver import Solver


def clear(path_to_board, path_to_command):
    with open(path_to_board, 'w') as board:
        board.write("")
    with open(path_to_command, 'w') as cmd:
        cmd.write("")



clear("board.out", "command.inp")

solver = Solver(path_to_board="board.out", path_to_command="command.inp")
game = CovidGame(10, 10, board_filepath='board.out', command_filepath='command.inp')

play_game = Process(target = game.play)
solve = Process(target = solver.solve)

play_game.start()
solve.start()