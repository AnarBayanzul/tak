# A lot of code was taken from AI assignment 3 Isola
import math, copy
infinity = math.inf

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
            # TODO: for custom board, update custom stone and capstone count
        #self.to_move = to_move
        # self.moves = self.listMoves(self.board, self.to_move, firstTurn, self.gameStones)[0] # Note: I don't really think implementing this line is necessary

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

    def listMoves(self, board, boardStoneCount, player, firstTurn):
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
        return lm
    
    def result(self, board, boardStoneCount, candidate:move, player, firstTurn):
        """Resulting board state from move"""
        newBoard = copy.deepcopy(board)
        newBoardStoneCount = copy.deepcopy(boardStoneCount)
        # If a placement move
        if candidate.count == 0:
            if candidate.stone == "F" or candidate.stone == "S":
                newBoardStoneCount[candidate.color + "S"] -= 1
            elif candidate.stone == "C":
                newBoardStoneCount[candidate.color + "C"] -= 1
            newBoard[candidate.column][candidate.row][0] = candidate.color + candidate.stone
        else: # If a movement move
            height = self.topValue(newBoard, candidate.column, candidate.row)[0]
            pickedUp = newBoard[candidate.column][candidate.row][height - candidate.count:height]
            for i in range(height - candidate.count, height):
                newBoard[candidate.column][candidate.row][i] = "  "
            if candidate.direction == '>':
                for x in range(1, len(candidate.deposit) + 1):
                    height = self.topValue(newBoard, candidate.column + x, candidate.row)[0]
                    newBoard[candidate.column + x][candidate.row][height:height + candidate.deposit[x - 1]] = pickedUp[:candidate.deposit[x - 1]]
                    pickedUp = pickedUp[candidate.deposit[x - 1]:]
            elif candidate.direction == '<':
                for x in range(1, len(candidate.deposit) + 1):
                    height = self.topValue(newBoard, candidate.column - x, candidate.row)[0]
                    newBoard[candidate.column - x][candidate.row][height:height + candidate.deposit[x - 1]] = pickedUp[:candidate.deposit[x - 1]]
                    pickedUp = pickedUp[candidate.deposit[x - 1]:]
            elif candidate.direction == '+':
                for z in range(1, len(candidate.deposit) + 1):
                    height = self.topValue(newBoard, candidate.column, candidate.row + z)[0]
                    newBoard[candidate.column][candidate.row + z][height:height + candidate.deposit[z - 1]] = pickedUp[:candidate.deposit[z - 1]]
                    pickedUp = pickedUp[candidate.deposit[z - 1]:]
            else:
                for z in range(1, len(candidate.deposit) + 1):
                    height = self.topValue(newBoard, candidate.column, candidate.row - z)[0]
                    newBoard[candidate.column][candidate.row - z][height:height + candidate.deposit[z - 1]] = pickedUp[:candidate.deposit[z - 1]]
                    pickedUp = pickedUp[candidate.deposit[z - 1]:]
        # Remember for, list of drops, first one is NOT how many to keep at initial square, always 0 kept at initial
        #      (boardState, boardStoneCount)
        return (newBoard, newBoardStoneCount, (player == "w") * "b" + (player == "b") * "w", ((player == "w") and firstTurn))
    
    def topBoard(self, board):
        """Return a 2D board showing just the top stone of every tile"""
        output = []
        for x in range(len(board)):
            column = []
            for z in range(len(board[0])):
                stone = self.topValue(board, x, z)[1]
                value = (stone[1] == "F" or stone[1] == "C") * stone[0] + (stone == "  " or stone[1] == "S") * " "
                column.append(value)
            output.append(column)
        return output



    def utility(self, board, boardStoneCount, player_perspective, player_to_move, weights = [3.0, 1.0, 1.0]):
        """The value of this terminal state to player (AKA heuristic)"""
        # First check for win:
        top = self.topBoard(board)
        whiteWin, blackWin = self.checkPaths(top)
        # If double, then active player wins
        if all([whiteWin, blackWin]):
            if player_to_move == player_perspective:
                return -infinity   
            else:
                return infinity     
        # + is good for player, - is bad for player
        if player_perspective == "w":
            if whiteWin:
                return infinity
            if blackWin:
                return -infinity
        else:
            if whiteWin:
                return -infinity
            if blackWin:
                return infinity

        # Count what stones are on top on the board
        inGameStones = {
            "wF": 0,
            "bF": 0,
            "wS": 0,
            "bS": 0,
            "wC": 0,
            "bC": 0,
            "  ": 0
        }
        capStoneHeights = {
            "wC": [],
            "bC": []
        }
        for x in range(self.boardSize):
            for z in range(self.boardSize):
                height, value = self.topValue(board, x, z)
                inGameStones[value] += 1
                if value in capStoneHeights.keys():
                    capStoneHeights[value].append(height)
        # Positive if white wins, negative if black
        score = inGameStones["wF"] - inGameStones["bF"]
        # Now check for full board OR for stones running out
        if inGameStones["  "] == 0 or boardStoneCount["wS"] == 0 or boardStoneCount["bS"] == 0:
            if score == 0:
                return 0
            if player_perspective == "w":
                return score * infinity
            else:
                return -score * infinity
        
        # Now apply heuristic
        # Factors:
        #   Who has more tiles on the board
        #   Who has taller capstone
        #   Who has more stones on top
        hTotalTileCount = boardStoneCount["bS"] + boardStoneCount["bC"] - boardStoneCount["wS"] - boardStoneCount["wC"]
        hCapstoneHeights = sum(capStoneHeights["wC"]) - sum(capStoneHeights["bC"])
        hTopCount = inGameStones["wF"] + inGameStones["wS"] + inGameStones["wC"] - (inGameStones["bF"] + inGameStones["bS"] + inGameStones["bC"])
        score = hTotalTileCount * weights[0] + hCapstoneHeights * weights[1] + hTopCount *weights[2]
        # Add to score if they have a capstone
        score += (inGameStones["wC"] - inGameStones["bC"]) * weights[1]
        return score * (player_perspective == "w") - score * (player_perspective == "b")

    def checkPaths(self, top):
        """Check if this position has a complete road"""
        size = len(top)
        vertLines = top[0]
        horiLines = [top[j][0] for j in range(size)]
        for i in range(len(top)):
            column = top[i]
            row = [top[j][i] for j in range(size)]
            # Check if path carries to next layer
            newVertLines = [" " for _ in range(size)]
            newHoriLines = [" " for _ in range(size)]
            for i in range(size):
                if vertLines[i] != "  " and vertLines[i] == column[i]:
                    newVertLines[i] = vertLines[i]
                if horiLines[i] != "  " and horiLines[i] == row[i]:
                    newHoriLines[i] = horiLines[i]
            # Now check for path bending
            # For every path in newLines
            for i in range(size):
                # Check above and below every potential path
                if newVertLines[i] != " ":
                    lesser = i - 1
                    if lesser >= 0:
                        while column[lesser] == newVertLines[i]:
                            newVertLines[lesser] = newVertLines[i]
                            lesser -= 1
                            if lesser < 0:
                                break
                    greater = i + 1
                    if greater < size:
                        while column[greater] == newVertLines[i]:
                            newVertLines[greater] = newVertLines[i]
                            greater += 1
                            if greater >= size:
                                break
                # Check above and below every potential path
                if newHoriLines[i] != " ":
                    lesser = i - 1
                    if lesser >= 0:
                        while row[lesser] == newHoriLines[i]:
                            newHoriLines[lesser] = newHoriLines[i]
                            lesser -= 1
                            if lesser < 0:
                                break
                    greater = i + 1
                    if greater < size:
                        while row[greater] == newHoriLines[i]:
                            newHoriLines[greater] = newHoriLines[i]
                            greater += 1
                            if greater >= size:
                                break
            vertLines = newVertLines
            horiLines = newHoriLines
        
        whiteWin = ("w" in vertLines) or ("w" in horiLines)
        blackWin = ("b" in vertLines) or ("b" in horiLines)
        return (whiteWin, blackWin)

    def is_terminal(self, board, boardStoneCount):
        """Check if game has ended in this state"""
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
        top = self.topBoard(board) # Every entry is either "w", "b", or " "
        if any(self.checkPaths(top)):
            return True
        return False

def play_game(game, strategies: dict, verbose = False, state = None):
    """Play a turn-taking game. `strategies` is a {player_name: function} dict,
    where function(state, game) is used to get the player's move."""

    if state == None:
        # board, stones, player perspective, player to move, first turn
        state = (game.board, game.gameStones, "w", "w", True)
    if verbose:
        print("initial state")
        print("to move: ", state[3])
        printBoard(state[0])
    while not game.is_terminal(state[0], state[1]):
        move = strategies[state[2]](game, state)
        if verbose:
            print('Player:', state[2], 'move:', move)
        state = game.result(state[0], state[1], move, state[2], state[4])
        state = list(state)
        state.insert(2, state[2])
        state = tuple(state)
        if verbose:
            printBoard(state[0])
    uf = game.utility(state[0], state[1], 'w', state[3])
    if verbose:
        print('End-of-game state')
        printBoard(state[0])
        print('End-of-game utility: {0}'.format(uf))
    return state, uf

# Alphabeta_search
def alphabeta_search(game, state, depth = 3):
    """Search game to determine best action; use alpha-beta pruning.
    As in [Figure 5.7], this version searches all the way to the leaves."""
    def max_value(state, alpha, beta, depth):
        # State is:
        # Board, stones, player perspective, then player to move, then first turn
        if depth <= 0:
            return game.utility(state[0], state[1], state[2], state[3]), None
        if game.is_terminal(state[0], state[1]):
            return game.utility(state[0], state[1], state[2], state[3]), None
        moves = game.listMoves(state[0], state[1], state[3], state[4])
        v, candidate = -infinity, moves[0]
        for a in moves:
            resultState = game.result(state[0], state[1], a, state[3], state[4])
            v2, _ = min_value((resultState[0], resultState[1], state[2], resultState[2], resultState[3]), alpha, beta, depth - 1)
            if v2 > v:
                v, candidate = v2, a
                alpha = max(alpha, v)
            if v >= beta:
                return v, candidate
        return v, candidate

    def min_value(state, alpha, beta, depth):
        if depth <= 0:
            return game.utility(state[0], state[1], state[2], state[3]), None
        if game.is_terminal(state[0], state[1]):
            return game.utility(state[0], state[1], state[2], state[3]), None
        moves = game.listMoves(state[0], state[1], state[3], state[4])
        v, candidate = +infinity, moves[0]
        for a in moves:
            resultState = game.result(state[0], state[1], a, state[3], state[4])
            v2, _ = max_value((resultState[0], resultState[1], state[2], resultState[2], resultState[3]), alpha, beta, depth - 1)
            if v2 < v:
                v, candidate = v2, a
                beta = min(beta, v)
            if v <= alpha:
                return v, candidate
        return v, candidate
    return max_value(state, -infinity, +infinity, depth)

def player(search_algorithm, depth):
    """A game player who uses the specified search algorithm"""
    return lambda game, state: search_algorithm(game, state, depth)[1]

def human_player(game, state):
    """Find some way to take input as move"""
    moves = game.listMoves(state[0], state[1], state[3], state[4])
    print(moves)
    index = int(input("Input your move: "))
    return moves[index]



depth = 5
result = play_game(tak(3), \
          {'w': player(alphabeta_search, depth), 'b': player(alphabeta_search, depth)}, \
          verbose=True)
if result[1] == 0:
    print("Draw")
elif result[1] < 0:
    print("Black wins")
else:
    print("White wins")
print(result[0][1])



# myGame = tak(2)
# theState = (myGame.board, myGame.gameStones, "w", True)
# for _ in range(5):
#     printBoard(theState[0])
#     print(theState[1])
#     searchResult = alphabeta_search(myGame, theState, 5)
#     print("Next move", searchResult)
#     print("Move perspective:", theState[2])
#     print()
#     print()
#     theState = myGame.result(theState[0], theState[1], searchResult[1], theState[2], theState[3])

# myGame = tak(2)
# myGame.board[0][0][0] = "bF"
# myGame.board[0][0][1] = "wF"
# myGame.gameStones["wS"] -= 1
# myGame.gameStones["bS"] -= 1
# printBoard(myGame.board)
# print(myGame.utility(myGame.board, myGame.gameStones, "w"))

# myGame = tak(2)
# myGame.board[0][0][0] = "bF"
# myGame.board[0][1][0] = "wF"
# myGame.gameStones["wS"] -= 1
# myGame.gameStones["bS"] -= 1
# printBoard(myGame.board)
# myMoves = myGame.listMoves(myGame.board, myGame.gameStones, "w", False)
# print(myMoves)
# for candidate in myMoves:
#     myResult = myGame.result(myGame.board, myGame.gameStones, candidate, "w", False)
#     print(candidate)
#     print(myGame.utility(myResult[0], myResult[1], "w"))
#     print("TO PLAY AFTER:(SHOULD BE B):", myResult[2])
