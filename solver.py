class Solver:
    def __init__(self, path_to_board: str = None, path_to_command: str = None):
        """
        `path_to_board`: path to the csv file containing data from the board.
        `path_to_command`: path to the csv file containing command (output from the solver)"""
        if path_to_board is None:
            path_to_board = "board.csv"
        self.board_path = path_to_board
        
        if path_to_command is None:
            path_to_command = "command.csv"
        self.iter = 0
        self.board_state = 