import setup

required  = {'numpy', 'ortools'}
setup.setup(required)

import config

from multiprocessing import Process
import subprocess


def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run_game():
    try:
        subprocess.run(["python", "game.py"])
    except FileNotFoundError:
        subprocess.run(["python3", "game.py"])

def run_solver():
    try:
        subprocess.run(["python", "solver.py"])
    except FileNotFoundError:
        subprocess.run(["python3", "solver.py"])

if __name__ == "__main__":
    while True:
        clear(config.board_path, config.cmd_path)
        game_process = Process(target=run_game)
        solver_process = Process(target=run_solver)
        game_process.start()
        solver_process.start()
        while game_process.is_alive() and solver_process.is_alive():
            pass