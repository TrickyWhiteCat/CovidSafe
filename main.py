from game import CovidGame
from solver import Solver


game = CovidGame(10, 10, board_filepath='board.csv', command_filepath='command.inp')
game.play()