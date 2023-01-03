#COVIDSafe

COVIDSafe helps quickly identify and contact people who may have been exposed to COVID-19 (called ‘close contacts’). The game will not protect you from viruses and will not warn you as soon as you get close to someone infected with a virus. You must try hard social distancing and access information about infected people.
## Idea
COVIDSafe is a classic puzzle game. The goal of the game is to clear a rectangle grid without exposing viruses. The viruses are hidden in some of the squares in the grids. When
each safe square is opened, a number indicating the number of viruses surrounding will appear and provide information to search for viruses.
##Rules of the game
Find all viruses in the grid by carefully revealing cells. A revealed cell will indicate the number of adjacent viruses (horizontally, vertically, or diagonally). Cells with no adjacent viruses will be blank and automatically reveal their neighbors. Revealing a virus will cause you to lose the game. You win the game by revealing all non-virus cells.
## How to run this game and its solver

Run `main.py` file and the game and its solver will automatically run. Noted that if your machine didn't have [ortools](https://developers.google.com/optimization) and [numpy](https://numpy.org/), they will be installed.

## Configuration
Head to `config.py` to modify run configuration:

- `board_path`: the file that our game writes down its state to and solver uses to read game state
- `cmd_path`: the file that our solver writes down commands to and the game uses to read commands.
- `first_pos`: position of the first cell to be revealed. If `None` then a random cell will be chosen.
- `wait`: the number of seconds that our solver will wait before writing down the next command.
- `timeout`: the amount of time (in seconds) that we wait for `CpSolver` to find all the solutions. If `None` then there will be no time limit.
- `board_size`: size of the game board
- `num_virus`: number of viruses