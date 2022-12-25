import numpy as np
import os

def creat_board():
    global virus_value
    global n
    print()
    print('\t\t======COVIDSafe======')
    print()
    print('    ', end = '')
    for i in range(n):
        if (i<9):
            print(str('0')+str(i+1), end = ' ')
        else:
            print(str(i+1), end = ' ')
    print()
    print('   ', end = '')
    for i in range(n):
        print('___', end = '')
    print('_')
    for row in range(n):
        if (row<9):
            print(str('0'+str(row+1)), end = ' ')
        else:
            print(str(row+1), end = ' ')
        for col in range(n):
            print('|'+ ' '+str(virus_value[row][col]),end='')
        print('|')
    print()


def creat_value():
    global n
    global virus
    global values

    lst0 = [0 for i in range(n*n-virus)]
    lst1 = [-1 for i in range(virus)]

    # Place Virus randomly using numpy.permutation
    arr = np.array(lst0+lst1)
    arr2 = np.random.permutation(arr)
    arr3 = arr2.reshape(n,n)
    values = arr3.tolist()

    # Set values
    for row in range(n):
        for col in range(n):

            # Skip if this cell is virus
            if values[row][col] == -1:
                continue
            
            if row > 0 and values[row-1][col] == -1:
                values[row][col] += 1

            if col > 0 and values[row][col-1] == -1:
                values[row][col] += 1
            
            if row < n-1 and values[row+1][col] == -1:
                values[row][col] += 1
            
            if col < n-1 and values[row][col+1] == -1:
                values[row][col] += 1

            if row > 0 and col > 0 and values[row-1][col-1] == -1:
                values[row][col] += 1

            if row > 0 and col < n-1 and values[row-1][col+1] == -1:
                values[row][col] += 1

            if row < n-1 and col > 0 and values[row+1][col-1] == -1:
                values[row][col] += 1

            if row < n-1 and col < n-1 and values[row+1][col+1] == -1:
                values[row][col] += 1


def check_over():
    global n
    global virus
    global virus_value
    count = 0

    # If open all number: non-zero, non-virus. Example: 1,2,3,4,...8
    for row in range(n):
        for col in range(n):
            if virus_value[row][col] != ' ' and virus_value[row][col] != 'M':
                count = count + 1
    if count == n*n-virus:
        return True
    else:
        return False


def clear():
    os.system('cls||clear')


def neighbours(row,col):
    global values
    global virus_value
    global visited
    if [row,col] not in visited:
        visited.append([row,col])

        if values[row][col] == 0:
            virus_value[row][col] = values[row][col]

            if row>0:
                neighbours(row-1,col)
            if col>0:
                neighbours(row,col-1)
            if row<n-1:
                neighbours(row+1,col)
            if col<n-1:
                neighbours(row,col+1)
            if row>0 and col>0:
                neighbours(row-1,col-1)
            if row<n-1 and col<n-1:
                neighbours(row+1,col+1)
            if row>0 and col<n-1:
                neighbours(row-1,col+1)
            if row<n-1 and col>0:
                neighbours(row+1,col-1)
        if values[row][col] != 0:
            virus_value[row][col] = values[row][col]


def instruction():
    print('Enter the value to open the cell:')
    print('Example: 3 4')
    print('Enter the value and letter \'M\' to mark the cell is virus:')
    print('Example: 4 5 M')
    print()


def show_virus():
    global n
    global values
    global virus_value
    for i in range(n):
        for j in range(n):
            if values[row][col] == -1:
                virus_value[row][col] = 'V'

if __name__ == '__main__':
    n = 16
    virus = 40
    values = [[0 for i in range(n)] for j in range(n)]
    virus_value = [[' ' for i in range(n)] for j in range(n)]
    marking = []
    creat_value()
    instruction()
    over = False

    while not over:
        creat_board()
        user_input = input('Enter the row and column separated by space: ').split()

        if len(user_input) == 2:
            try:
                val = list(map(int,user_input))
            except ValueError:
                clear()
                print('Wrong input!')
                instruction()
                continue
        
        elif len(user_input) == 3:
            if user_input[2] != 'M' and user_input[2] != 'm':
                clear()
                print('Wrong input!')
                instruction()
                continue
            try:
                val = list(map(int,user_input[:2]))
            except ValueError:
                clear()
                print('Wrong input!')
                instruction()
                continue

            if val[0]<1 or val[1]<1 or val[0]>n or val[1]>n:
                clear()
                print('Wrong input!')
                instruction()
                continue 
            
            # Standardlize user_input:
            row = val[0]-1
            col = val[1]-1

            if [row,col] in marking: # This cell already set
                clear()
                print('Virus is already set!')
                continue

            if virus_value[row][col] != ' ': # This cell already known
                clear()
                print('This cell is already know!')
                continue
            
            if len(marking) < virus:
                clear()
                marking.append([row,col])
                virus_value[row][col] = 'M'
                continue
            else:
                clear()
                print('Marking finished!')
                continue
        
        else: # Wrong input
            clear()
            print('Wrong input!')
            instruction()
            continue

        if val[0]<1 or val[1]<1 or val[0]>n or val[1]>n:
                clear()
                print('Wrong input!')
                instruction()
                continue 
        
        row = val[0]-1
        col = val[1]-1
        
        # Unflag if already flagged
        if [row,col] in marking:
            marking.remove([row,col])
        
        # Game over
        if values[row][col] == -1: 
            virus_value[row][col] = 'V'
            show_virus()   
            creat_board()
            print('GAME OVER!!!')
            over = True
            continue
        
        elif values[row][col] == 0:
            visited = []
            virus_value[row][col] = '0'
            neighbours(row,col)
        
        else:
            virus_value[row][col] = values[row][col]
        
        if (check_over()):
            show_virus()
            creat_board()
            print('YOU WIN!!!')
            over = True