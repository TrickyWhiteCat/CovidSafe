import logging


logging.basicConfig(filename='logger.log')
class Solver:
    def __init__(self, path_to_board: str = None, path_to_command: str = None):
        """
        `path_to_board`: path to the csv file containing data from the board.
        `path_to_command`: path to the csv file containing command (output from the solver)"""
        if path_to_board is None:
            path_to_board = "board.out"
        self.board_path = path_to_board
        
        if path_to_command is None:
            path_to_command = "command.inp"
        self.command_path = path_to_command
        self.iter = 1

    def read_board(self):
        path = self.board_path
        while True: # Wait for the file to be updated
            with open(path, mode='r') as board:
                try:
                    iter = int(board.readline())
                    if iter < self.iter:
                        board_state = [line.split(",") for line in board.readlines()]
                        self.board_state = board_state
                        logging.info("fine")
                        return
                except ValueError:
                    pass

    def write_command(self):
        import random
        with open(self.command_path, mode = 'w') as cmd:
            #self.read_board()
            cmd.write(f"{self.iter}\n")
            cmd.write(f"{' '.join([str(val) for val in random.choices(range(1, 11), k = 2)])}")
            self.iter += 1
            cmd.close()

    def solve(self):
        import time
        while True:
            time.sleep(1)
            self.write_command()