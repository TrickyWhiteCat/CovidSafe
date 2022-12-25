import random
import time


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
        self.__iter = 1
        self.solved = False
        self.__finished = False

    def __read_board(self):
        path = self.board_path
        while True: # Wait for the file to be updated
            with open(path, mode='r') as board:
                try:
                    iter = int(board.readline())
                    if iter < self.__iter:
                        board_state = [line.split(",") for line in board.readlines()]
                        self.__board_state = board_state
                        return
                except ValueError:
                    pass

    def __write_command(self, row, col):
        with open(self.command_path, mode = 'w') as cmd:
            cmd.write(f"{self.__iter}\n")
            cmd.write(f"{row} {col}")
            self.__iter += 1
            cmd.close()

    def __choose_pos(self):
        return random.randint(1, 10), random.randint(1, 10)

    def __check_finished(self):
        for row in self.__board_state:
            if "V" in row: # Virus detected
                self.solved = False
                self.__finished = True
                return
        
        for row in self.__board_state:
            if " " in row: # There exists unopened cell
                self.__finished = False
                return

        # No unopened cell left
        self.__finished = True
        self.solved = True


    def solve(self):
        while not self.__finished:
            self.__read_board()
            row, col = self.__choose_pos()
            self.__write_command(row = row, col = col)
            self.__check_finished()
        
        with open("result.txt", 'a') as res_file:
            res_file.write(f"{int(self.solved)}\n")