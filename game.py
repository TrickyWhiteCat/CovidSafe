import numpy as np
import os

import config

class CovidGame:
    def __init__(self, board_size, num_virus, board_filepath = None, command_filepath = None):
        self.board_size = board_size
        self.num_virus = num_virus
        self.num_virus_left = num_virus
        self.board_filepath = board_filepath
        self.command_filepath = command_filepath

        self.values = [[0 for i in range(board_size)] for j in range(board_size)]
        self.virus_values = [[' ' for i in range(board_size)] for j in range(board_size)]
        self.marking = []
        self.visited = []
        self.clear()
        self.creat_value()
        self.instruction()
        self.over = False
        self.iter = 0

    def creat_board(self):
        
        
        print('\t\t======COVIDSafe======')
        
        print('    ', end = '')
        for i in range(self.board_size):
            if (i<9):
                print(str('0')+str(i+1), end = ' ')
            else:
                print(str(i+1), end = ' ')
        
        print('\n   ', end="")
        for i in range(self.board_size):
            print('___', end = '')
        print('_')
        for row in range(self.board_size):
            if (row<9):
                print(str('0'+str(row+1)), end = ' ')
            else:
                print(str(row+1), end = ' ')
            for col in range(self.board_size):
                print('|'+ ' '+str(self.virus_values[row][col]),end='')
            print('|')
        
        
        if self.board_filepath is not None:
            self.to_csv()

    def creat_value(self):

        lst0 = [0 for i in range(self.board_size*self.board_size-self.num_virus)]
        lst1 = [-1 for i in range(self.num_virus)]

        # Place Virus randomly using numpy.permutation
        arr = np.array(lst0+lst1)
        arr2 = np.random.permutation(arr)
        arr3 = arr2.reshape(self.board_size,self.board_size)
        self.values = arr3.tolist()

        # Set values
        for row in range(self.board_size):
            for col in range(self.board_size):

                # Skip if this cell is virus
                if self.values[row][col] == -1:
                    continue
                
                if row > 0 and self.values[row-1][col] == -1:
                    self.values[row][col] += 1

                if col > 0 and self.values[row][col-1] == -1:
                    self.values[row][col] += 1

                if row < self.board_size-1 and self.values[row+1][col] == -1:
                    self.values[row][col] += 1

                if col < self.board_size-1 and self.values[row][col+1] == -1:
                    self.values[row][col] += 1

                if row > 0 and col > 0 and self.values[row-1][col-1] == -1:
                    self.values[row][col] += 1

                if row > 0 and col < self.board_size-1 and self.values[row-1][col+1] == -1:
                    self.values[row][col] += 1

                if row < self.board_size-1 and col > 0 and self.values[row+1][col-1] == -1:
                    self.values[row][col] += 1

                if row < self.board_size-1 and col < self.board_size-1 and self.values[row+1][col+1] == -1:
                    self.values[row][col] += 1

    def check_over(self):
        count = 0

        # If open all number: non-zero, non-virus. Example: 1,2,3,4,...8
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.virus_values[row][col] != ' ' and self.virus_values[row][col] != 'M':
                    count = count + 1
        if count == self.board_size*self.board_size-self.num_virus:
            return True
        else:
            return False

    def clear(self):
        os.system('cls||clear')

    def neighbours(self, row, col):
        if [row,col] not in self.visited:
            self.visited.append([row,col])

            if self.values[row][col] == 0:
                self.virus_values[row][col] = self.values[row][col]

                if row > 0:
                    self.neighbours(row-1,col)
                if col > 0:
                    self.neighbours(row,col-1)
                if row < self.board_size-1:
                    self.neighbours(row+1,col)
                if col < self.board_size-1:
                    self.neighbours(row,col+1)
                if row > 0 and col > 0:
                    self.neighbours(row-1,col-1)
                if row < self.board_size-1 and col < self.board_size-1:
                    self.neighbours(row+1,col+1)
                if row > 0 and col < self.board_size-1:
                    self.neighbours(row-1,col+1)
                if row < self.board_size-1 and col > 0:
                    self.neighbours(row+1,col-1)
            if self.values[row][col] != 0:
                self.virus_values[row][col] = self.values[row][col]

    def instruction(self):
        pass
        print('Enter the value to open the cell:')
        print('Example: 3 4')
        print('Enter the value and letter \'M\' to mark or unmark the cell as virus:')
        print('Example: 4 5 M')
        


    def show_virus(self):
        for row in range(self.board_size):
            for col in range(self.board_size):
                if self.values[row][col] == -1:
                    self.virus_values[row][col] = 'V'

    def to_csv(self):
        with open(file=self.board_filepath, mode='w') as f:
            f.write(f"{self.iter} {self.num_virus_left}\n")
            for row in self.virus_values:
                f.write(f'{",".join([str(val) for val in row])}\n')

    def get_input(self):
        '''Support 2 type of control: via command line or via input from file.'''
        if self.command_filepath:
            while True: # Wait until the file is updated
                with open(self.command_filepath, 'r') as f:
                    try:
                        iter = int(f.readline())
                        if iter > self.iter:
                            return f.readline().split(' ')
                        f.close()
                    except ValueError:
                        pass
        
        return input("Enter the row and column separated by space: ").split()
                

    def play(self):
        while not self.over:
            self.creat_board()
            user_input = self.get_input()
            self.iter += 1

            if len(user_input) == 2:
                try:
                    self.clear()
                    val = list(map(int,user_input))
                except ValueError:
                    self.clear()
                    print('Wrong input!')
                    self.instruction()
                    continue
                
            elif len(user_input) == 3:
                if user_input[2] != 'M' and user_input[2] != 'm':
                    self.clear()
                    print('Wrong input!')
                    self.instruction()
                    continue
                try:
                    val = list(map(int,user_input[:2]))
                except ValueError:
                    self.clear()
                    print('Wrong input!')
                    self.instruction()
                    continue

                if val[0] < 1 or val[1] < 1 or val[0] > self.board_size or val[1] > self.board_size:
                    self.clear()
                    print('Wrong input!')
                    self.instruction()
                    continue 
                
                # Standardlize user_input:
                row = val[0]-1
                col = val[1]-1

                if [row,col] in self.marking: # Unmark marked cell
                    self.clear()
                    self.marking.remove([row, col])
                    self.virus_values[row][col] = ' '
                    continue

                if self.virus_values[row][col] != ' ': # This cell already known
                    self.clear()
                    print('This cell is already know!')
                    continue
                
                if len(self.marking) < self.num_virus:
                    self.clear()
                    self.marking.append([row,col])
                    self.virus_values[row][col] = 'M'
                    self.num_virus_left -= 1
                    continue
                else:
                    self.clear()
                    print('Marking finished!')
                    continue
                
            else: # Wrong input
                self.clear()
                print(f'Input are too long!')
                self.instruction()
                continue

            if val[0] < 1 or val[1] < 1 or val[0] > self.board_size or val[1] > self.board_size:
                    self.clear()
                    print('Wrong input!')
                    print(f"{val[0]}, {val[1]} ")
                    self.instruction()
                    continue 
                
            row = val[0]-1
            col = val[1]-1

            # Unflag if already flagged
            if [row,col] in self.marking:
                self.marking.remove([row,col])

            # Game over
            if self.values[row][col] == -1: 
                self.virus_values[row][col] = 'V'
                self.show_virus()   
                self.creat_board()
                print('GAME OVER!!!')
                self.over = True
                continue
            
            elif self.values[row][col] == 0:
                self.visited = []
                self.virus_values[row][col] = '0'
                self.neighbours(row,col)

            else:
                self.virus_values[row][col] = self.values[row][col]

            if (self.check_over()):
                self.show_virus()
                self.creat_board()
                print('YOU WIN!!!')
                self.over = True
        input("Press enter to exit.")

def main():
    game = CovidGame(board_size=config.board_size,
                    num_virus=config.num_virus,
                    board_filepath=config.board_path,
                    command_filepath=config.cmd_path)
    game.play()

if __name__ == "__main__":
    main()