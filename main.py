from multiprocessing import Process
import subprocess
import os

import config

def clear(*files):
    for filename in files:
        with open(filename, 'w') as file:
            file.write("")

def run_game():
    subprocess.run(["python", "game.py"], shell=True)

def run_solver():
    subprocess.run(["python", "solver.py"], shell=True)

if __name__ == "__main__":
    clear(config.board_path, config.cmd_path)
    os.system("wt python solver.py")
    os.system("wt python game.py")
