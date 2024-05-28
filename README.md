# tak
BFS engine for searching Tak using alpha-beta pruning, multiple custom heuristics, and simulated annealing to tune the weighting of the heuristics.

## What is tak
Tak is an abstract board game similar to chess where two players try to compet in building a road from one side of the board to the other first. Not many resources exist for learning and improving in the game so I made a AI search engine for it.

For more info on Tak, [click here.](https://en.wikipedia.org/wiki/Tak_(game))

## Heuristics
I have three heuristics for estimating the value of a nonterminal position. These are purposely very lightweight and simple heuristics, so they are not going to be accurate, just good rules of thumb. The heuristics are:
1. Score based on who has more tiles on the board
2. Score based on who has a taller capstone
3. Score based on who controls more spaces on the board

Simulated annealing suggests that weightings of `[0.6, 0.5, 0.7]` for each heuristic are the most promising.

# How to run
There are two parts to this, there is just the python script that is implementing the actual engine, and also a three.js scene showing it graphically.

## The engine
To run the code you will need the python libraries `math`, `copy`, `random`, `tqdm`, `matplotlib`, and `numpy`.

So there are three pre-built function you can just run with no other input needed.
1. `playAgainstComputer()`: you can specify a depth and weighting for the alpha-beta search and a board size and you can play against the AI.
2. `AIvsAI()`: same specifications as above, you can watch two AIs duke it out.
3. `simulatedAnnealing()`: Run simulated annealing to find optimal weightings.

## The Graphics
If you want to run the graphics using three.js, then you need to download node.js. Then, go to the directory for the project, and download three.js with the command `npm install --save three`, then install vite with `npm install --save-dev vite`, which will host the site. Now type `npx vite` to host the site and navigate to the link given by the console command.

# Interpreting the Engine
The python script has two classes, one for the actual game of Tak, and one for the possible moves. The class for move is basically a data structure for holding the information required to define any one move. The game class sets up an initial board and stones, and has methods to check whether the game has ended, who's won, the list of possible moves from a given board state, how a move will affect a board state, and an estimate of how good a given board state is. (heuristic)

The `printBoard()` function is used to display the board in a human readable format. The board itself is setup as a 3D list (index order is x, z, then y) where each pair of x and z values specify a location on the board while the y value specifies height. (For stacks of tiles) The function prints the board's cross section, showing what tiles are in which location until you get to a value of y, where there are no tiles. So the left most printed square, is the board at height 0, and the board to its right is at height 1, and etc.
