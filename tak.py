# A lot of code was taken from AI assignment 3 Isola
import math, copy

def printBoard(board):
    """
    The board is a 3D list where it is indexed by x, then z, then y value
    Every entry in the board first has a character for color, ('w' for white or 'b' for black), then a character for type. ('F' for flat, 'S' for standing, 'C' for capstone)
    Note: (0, 0 , 0) is top left
    """
    tallest = 0
    for x in range(len(board)):
        for z in range(len(board[0])):
            for y in range(len(board[0][0])):
                if board[x][z][y] != "  " and tallest < y:
                    tallest = y
    output = ""
    for z in range(len(board[0])):
        outputLine = "||"
        for y in range(tallest + 1):
            for x in range(len(board)):
                outputLine += board[x][z][y] + '|'
            outputLine += "| ||"
        output += outputLine[0:-3] + "\n"
    borderLine = "+="
    for _ in range(tallest + 1):
        for _ in range(len(board)):
            borderLine += "==="
        borderLine += "+ +="
    borderLine = borderLine[0:-2] + "\n"
    output = borderLine + output + borderLine
    print(output, end="")

# Abstract class for a game
class Game:
    """A game is similar to a problem, but it has a utility for each
    state and a terminal test instead of a path cost and a goal
    test. To create a game, subclass this class and implement actions,
    result, utility, and terminal_test. You may override display and
    successors or you can inherit their default methods. You will also
    need to set the .initial attribute to the initial state; this can
    be done in the constructor."""

    def actions(self, state):
        """Return a list of the allowable moves at this point."""
        raise NotImplementedError

    def result(self, state, move):
        """Return the state that results from making a move from a state."""
        raise NotImplementedError

    def utility(self, state, player):
        """Return the value of this final state to player."""
        raise NotImplementedError

    def terminal_test(self, state):
        """Return True if this is a final state for the game."""
        return not self.actions(state)

    def to_move(self, state):
        """Return the player whose move it is in this state."""
        return state.to_move

    def display(self, state):
        """Print or otherwise display the state."""
        print(state)

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)
    
# Describe move
class move:
    """
    Every potential move can be characterized by
    (
        int pickupNum, or type of placement (0 means placement)
        int column (x),
        int row (z),
        char direction, (which way to move stones) <, >, +, -
        arr int [deposit stones], number of stones deposited at each location
        char stoneType (flat stones, standing stones or capstone) (F, S, C) (blank for movement)
        char color "w" or "b" (color of stone place, or color of top stone)
    )
    Note: < > is movement along x-axis (left right)
          + - is movement along z-axis (forward back)
    """
    def __init__(self, pickup: int, column: int, row: int, direction: str, deposit:list, stoneType:str, color:str):
        assert (pickup >= 0) and (row >= 0) and (column >= 0) and (direction in ['>', '<', '+', '-', ' ']) and (stoneType in ['F', 'S', 'C', ' ']) and (color in ['w', 'b']), \
            f"Something stupid happened\n {pickup}, {column}, {row}, {direction}, {deposit}, {stoneType}, {color}"
        self.count = pickup
        self.column = column
        self.row = row
        self.direction = direction
        self.deposit = deposit
        self.stone = stoneType
        self.color = color
    def __repr__(self):
        # This is verbose
        # return f"Move(pickupNum: {self.count}, x:{self.column}, z:{self.row}, dir:{self.direction}, deposit:{self.deposit}, type:{self.stone}, color:{self.color})"
        # This is shorter
        return f"({self.count},{self.column},{self.row},{self.direction}, {self.deposit}, {self.stone}, {self.color})"

# TAK game class
class tak(Game):
    stoneCounts    = [0,  0,  2, 10, 15, 21, 30, 40, 50]
    capstoneCounts = [0,  0,  0,  0,  0,  1,  1,  2,  2]
    def __init__(self, boardSize = 2, board = None, firstTurn = True, to_move = "w"):
        self.boardSize = boardSize
        self.maxHeight = 2 * self.stoneCounts[boardSize] + int(self.capstoneCounts[boardSize] > 0)
        # Board indexing is (x, z, y)
        self.gameStones = {}
        if board == None:
            self.board = [[['  ' for _ in range(self.maxHeight)] for _ in range(boardSize)] for _ in range(boardSize)]
            # S here stands for stones, not "standing"
            self.gameStones["wS"] = self.stoneCounts[boardSize]
            self.gameStones["bS"] = self.stoneCounts[boardSize]
            self.gameStones["wC"] = self.capstoneCounts[boardSize]
            self.gameStones["bC"] = self.capstoneCounts[boardSize]
        else:
            self.board = board
            # TODO: for custom board, update custome stone and capstone count
        self.to_move = to_move
        self.moves = self.listMoves(self.board, self.to_move, firstTurn, self.gameStones)[0] # Note: I don't really think implementing this line is necessary

    def topValue(self, board, x, z):
        """Return height and top stone of board space"""
        height = 0
        for y in range(self.boardSize):
            # Max height for pickup is size of board
            if board[x][z][y] == '  ' or height >= self.boardSize:
                break
            else:
                height += 1
        return height, board[x][z][height - 1]

    def listMoves(self, board, player, firstTurn, boardStoneCount):
        """List legal moves for a given board state"""
        lm = []
        # For every square
        for x in range(self.boardSize):
            for z in range(self.boardSize):
                # Placement moves
                if board[x][z][0] == "  ":
                    if firstTurn: # Enemy road if turn 1
                        lm.append(move(0, x, z, ' ', [], 'F', ('w' == player) * 'b' + ('b' == player) * 'w'))
                    else: # Capstone, wall, or road
                        if boardStoneCount[player + "S"] > 0:
                            lm.append(move(0, x, z, ' ', [], 'F', player))
                            lm.append(move(0, x, z, ' ', [], 'S', player))
                        if boardStoneCount[player + "C"] > 0:
                            lm.append(move(0, x, z, ' ', [], 'C', player))
                else:
                    # Movement moves
                    # if first turn, then no movement
                    if firstTurn:
                        continue
                    # Find height of current square
                    height, topStone = self.topValue(board, x, z)
                    # Check if top is controlled by player
                    if topStone[0] != player:
                        continue
                    # Loop through direction
                    for dir in ['>', '<', '+', '-']:
                        # Check how far you can travel in that direction (1 means stay in place)
                        maxTravelLength = 1
                        lastMustCrush = False
                        if dir == '>':
                            for xMove in range(x + 1, self.boardSize):
                                currentTopStone = self.topValue(board, xMove, z)[1]
                                # Check if wall or capstone get in way
                                if currentTopStone[1] == "C":
                                    break
                                elif currentTopStone[1] == "S":
                                    if topStone[1] == "C":
                                        # Wall Crush shenaningans makes it possible, but must end there
                                        lastMustCrush = True
                                        maxTravelLength += 1
                                        break
                                    else:
                                        break
                                else: # Where top stone is "F" or " "
                                    maxTravelLength += 1
                        elif dir == '<':
                            for xMove in range(x - 1, -1, -1):
                                currentTopStone = self.topValue(board, xMove, z)[1]
                                # Check if wall or capstone get in way
                                if currentTopStone[1] == "C":
                                    break
                                elif currentTopStone[1] == "S":
                                    if topStone[1] == "C":
                                        # Wall Crush shenaningans makes it possible, but must end there
                                        lastMustCrush = True
                                        maxTravelLength += 1
                                        break
                                    else:
                                        break
                                else: # Where top stone is "F" or " "
                                    maxTravelLength += 1
                        elif dir == '+':
                            for zMove in range(z + 1, self.boardSize):
                                currentTopStone = self.topValue(board, x, zMove)[1]
                                # Check if wall or capstone get in way
                                if currentTopStone[1] == "C":
                                    break
                                elif currentTopStone[1] == "S":
                                    if topStone[1] == "C":
                                        # Wall Crush shenaningans makes it possible, but must end there
                                        lastMustCrush = True
                                        maxTravelLength += 1
                                        break
                                    else:
                                        break
                                else: # Where top stone is "F" or " "
                                    maxTravelLength += 1
                        elif dir == '-':
                            for zMove in range(z - 1, -1, -1):
                                currentTopStone = self.topValue(board, x, zMove)[1]
                                # Check if wall or capstone get in way
                                if currentTopStone[1] == "C":
                                    break
                                elif currentTopStone[1] == "S":
                                    if topStone[1] == "C":
                                        # Wall Crush shenaningans makes it possible, but must end there
                                        lastMustCrush = True
                                        maxTravelLength += 1
                                        break
                                    else:
                                        break
                                else: # Where top stone is "F" or " "
                                    maxTravelLength += 1
                        if maxTravelLength == 1: # Can't move any pieces
                            continue
                        # Loop through pickup number
                        for pickupCount in range(1, height + 1):
                            # Loop through every combination of dropoff for maxTravelLength
                            for travelLength in range(1, maxTravelLength):
                                dropoffs = [1 for _ in range(travelLength)]
                                stonesUsed = sum(dropoffs)
                                if stonesUsed > pickupCount: # Num of pickups can't account for long travel length
                                    break
                                elif stonesUsed == pickupCount: # dropoffs list is already done
                                    # Add move
                                    lm.append(move(pickupCount, x, z, dir, dropoffs, " ", topStone[0]))
                                else: # dropoff list does not have number of dropoffs equal to pickup Count
                                    # Find every combination of spreading the extra stones across the dropoffs list
                                    extraStones = pickupCount - stonesUsed
                                    # Check if maxTravelLength and lastMustCrush
                                    # Just means that lost dropoff has to be a single tile.
                                    spaces = travelLength - int(travelLength == maxTravelLength and lastMustCrush)
                                    dropOffModifications = [[0 for _ in range(travelLength)]]
                                    for _ in range(extraStones):
                                        newModifications = []
                                        for modification in dropOffModifications:
                                            for space in range(spaces):
                                                toAdd = modification.copy()
                                                toAdd[space] += 1
                                                if toAdd not in newModifications:
                                                    newModifications.append(toAdd)
                                        dropOffModifications = newModifications
                                    # dropOffModifications consists of a list of every possible way to spread the extra stones
                                    for modification in dropOffModifications:
                                        finalDropoff = [i + j for i, j in zip(dropoffs, modification)]
                                        #finalDropoff = map(sum, zip(dropoffs, dropOffModifications))
                                        lm.append(move(pickupCount, x, z, dir, finalDropoff, " ", topStone[0]))
        # Return list of moves and whether it is still first turn.
        return lm, ((player == "w") and firstTurn)
    
    def result(self, board, boardStoneCount, candidate:move):
        """Resulting board state from move"""
        newBoard = copy.deepcopy(board)
        newBoardStoneCount = copy.deepcopy(boardStoneCount)
        # If a placement move
        if candidate.count == 0:
            newBoardStoneCount[candidate.color + "S"] -= 1
            newBoard[candidate.column][candidate.row][0] = candidate.color + candidate.stone
        else: # If a movement move
            # TODO
            pickedUp = []

            pass

        # Remember for, list of drops, first one is NOT how many to keep at initial square, always 0 kept at initial
        #      (boardState, boardStoneCount, validCheck)
        return (newBoard, newBoardStoneCount, True)
    
    def utility(self, board, boardStoneCount, player):
        """The value of this terminal state to player (AKA heuristic)"""
        # TODO
        # If player has won, which player (+infinity or -infinity)
        # + is good for player, - is bad for player
        pass
    def is_terminal(self, board, boardStoneCount):
        """Check if one player has won"""
        # If one player has run out of stones to play
        if boardStoneCount["wS"] == 0 or boardStoneCount["bS"] == 0:
            return True
        # If the board is entirely covered
        boardFull = True
        for x in range(len(board)):
            for z in range(len(board[0])):
                if board[x][z][0] == "  ":
                    boardFull = False
                    break
            if not boardFull:
                break
        if boardFull:
            return True
        # If there is a complete road
        # TODO: Check for complete road
        pass


def play_game(game, strategies: dict, verbose = False):
    """Play a turn-taking game. `strategies` is a {player_name: function} dict,
    where function(state, game) is used to get the player's move."""
    # TODO: this is copied from Isola, need to modify to work with Tak
    state = game.board
    if verbose:
        print("initial state")
        print(state)
    while not game.is_terminal(state):
        player = game.to_move
        move = strategies[player](game, state)
        state = game.result(state, move)
        if verbose:
            print('Player', player, 'move:', move)
            print(game.prettyboard(state.board))
    uf = game.utility(state,'w')
    if verbose:
        print('End-of-game state')
        game.display(state)
        print('End-of-game utility: {0}'.format(uf))
    return state,uf

infinity = math.inf
# Alphabeta_search
def alphabeta_search(game, state):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""

    player = state.to_move

    def max_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = -infinity, None
        for a in game.actions(state):
            v2, _ = min_value(game.result(state, a), alpha, beta)
            if v2 > v:
                v, move = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, move
        return v, move

    def min_value(state, alpha, beta):
        if game.is_terminal(state):
            return game.utility(state, player), None
        v, move = +infinity, None
        for a in game.actions(state):
            v2, _ = max_value(game.result(state, a), alpha, beta)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, move
        return v, move

    return max_value(state, -infinity, +infinity)

def player(search_algorithm):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state)[1]

def human_player():
    """Find some way to take input as move"""
    # TODO
    pass

# result = play_game(tak(3), \
#           {'w': human_player, 'b': player(alphabeta_search)}, \
#           verbose=False)
# if result[1] == 0:
#     print("Draw")
# elif result[1] < 0:
#     print("Player 2 wins")
# else:
#     print("Player 1 wins")
# print(result[0])
myGame = tak(3)
print(myGame.moves)

myGame.board[0][0][0] = "wF"
myGame.board[0][0][1] = "wF"
myGame.board[0][1][0] = "bS"
myGame.board[1][0][0] = "bS"
printBoard(myGame.board)

print(len(myGame.listMoves(myGame.board, "w", False)[0]))
print(myGame.listMoves(myGame.board, "w", False)[0])
