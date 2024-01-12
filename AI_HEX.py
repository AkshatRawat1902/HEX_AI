from random import random
from colorama import Fore, Style
import random

EMPTY = '.'
BLUE = 'B'
RED = 'R'
PLAYER = [BLUE, RED]
DEFAULT_SIZE = 5
FLAG = 0

#---------------------------------------------------------------------------HEX GAME OUTLINE---------------------------------------------------------------------------------------------------#
class Game:  

    def __init__(self, size):
        self.size = size
        self.board = [[EMPTY] * size for i in range(size)]
        self.ds = [-1] * (size * size + 4)
        self.turn = 0

    def root(self, a):       
        if self.ds[a] < 0:
            return a
        else:
            self.ds[a] = self.root(self.ds[a])
            return self.ds[a]

    def join(self, a, b):
        a, b = self.root(a), self.root(b)
        if a == b:
            return False
        if self.ds[a] < self.ds[b]:
            a, b = b, a
        self.ds[b] += self.ds[a]
        self.ds[a] = b
        return True
                    
    def current(self):      
        p =  PLAYER[self.turn]
        return p

    def checkInside(self, x, y, empty=False):
        return 0 <= x and x < self.size and 0 <= y and y < self.size

    def __getitem__(self, pos):
        x, y = pos
        GameError.test(self.checkInside(x, y), "Invalid move. Position <%d;%d> out of range." % (x, y))
        return self.board[x][y]

    def neighbour(self, x, y):
        self[x, y]
        neighborhood = [(-1, 1), (0, 1), (1, 0), (1, -1), (0, -1), (-1, 0)]

        for neig in neighborhood:
            nx, ny = x + neig[0], y + neig[1]
            if self.checkInside(nx, ny):
                yield nx, ny

    def position(self, x, y):
        return self.size * x + y + 4

    def play(self, x, y):
        value = self[x, y]
        GameError.test(value == EMPTY, "Invalid move.")

        self.board[x][y] = PLAYER[self.turn]

        if self.turn == 0:
            if y == 0:
                self.join(0, self.position(x, y))
            elif y + 1 == self.size:
                self.join(1, self.position(x, y))
        else:
            if x == 0:
                self.join(2, self.position(x, y))
            elif x + 1 == self.size:
                self.join(3, self.position(x, y))

        for nx, ny in self.neighbour(x, y):
            if self[nx, ny] == self[x, y]:
                self.join(self.position(nx, ny), self.position(x, y))

        self.turn ^= 1

    def clone_play(self, x, y):
        clone = self.__clone__()
        clone.play(x, y)
        return clone

    def winner(self):
        if self.root(0) == self.root(1):
            return PLAYER[0]
        if self.root(2) == self.root(3):
            return PLAYER[1]
        return EMPTY

    def __clone__(self):
        game = Game(self.size)
        game.board = [row[:] for row in self.board]
        game.ds = self.ds[:]
        game.turn = self.turn
        return game

    def __str__(self):
            flag0=0
            t=self.size *2
            ans = ""

            print(" ",end=" ")
            for i in range(self.size):
                print(Fore.RED+ str(i) + Style.RESET_ALL, end=" ")

            for i in range(self.size):
                if flag0==0:
                    print("")
                    print(Fore.RED +'  '+ '_' *t + Style.RESET_ALL)
                    flag0=1

                ans += (" " * i) + Fore.BLUE + str(i)+' \\' + Style.RESET_ALL
                for j in range(self.size):
                    if self[i, j] == 'B':
                        ans += Fore.BLUE + " %s" % self[i, j] + Style.RESET_ALL
                    elif self[i, j] == 'R':
                        ans += Fore.RED + " %s" % self[i, j] + Style.RESET_ALL
                    else:
                        ans += " %s" % self[i, j]

                    #ans += " %s" % self[i, j]
                ans += Fore.BLUE + ' \\' + Style.RESET_ALL  # Add blue slanting line at the end of each row
                ans += "\n"

            # Add a red dotted line at the end
            ans += Fore.RED + '   '+' ' * (self.size) + '_' * (t) + Style.RESET_ALL

            return ans

    def __repr__(self):
        return self.__str__()

class GameError(BaseException): 
    def test(value, e):
        # Assert
        if not value:
            raise GameError(e)
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------RANDOM AGENT---------------------------------------------------------------------------------------------------#
def randomAgent(game):
    available_moves = []

    for i in range(game.size):
        for j in range(game.size):
            if game[i, j] == EMPTY:
                available_moves.append((i, j))

    return random.choice(available_moves)

def possibleMoves(game):
    available_moves = []
    for i in range(game.size):
        for j in range(game.size):
            if game[i, j] == EMPTY:
                available_moves.append((i, j))

    return available_moves
#---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------MINIMAX WITH ALPHA BETA PRUNING----------------------------------------------------------------------------------------#
def minimaxAB(game, player, depth, h, moves):
    best, value = maxplay(game, None, player, depth, h, moves)
    return best

def maxplay(game, play, player, depth, h, moves, alpha=float('-inf'), beta=float('inf')):
    best = None
    best_value = float('-inf')

    if game.winner() != EMPTY:
        return play, -1
        # return play, 1 if game.winner() == player else -1

    if not depth:
        return play, h(game, player)

    for x, y in moves(game, player):
        b, value = minplay(game.clone_play(x, y), (x, y), player, depth - 1, h, moves)
        alpha = max(alpha, value)

        if alpha >= beta:
            break

        if value > best_value:
            best = (x, y)
            best_value = value

    return best, best_value

def minplay(game, play, player, depth, h, moves, alpha=float('-inf'), beta=float('inf')):
    best = None
    best_value = float('inf')

    if game.winner() != EMPTY:
        return play, 1
        # return play, 1 if game.winner() == player else -1

    if not depth:
        return play, h(game, player)

    for x, y in moves(game, player):
        _, value = maxplay(game.clone_play(x, y), (x, y), player, depth - 1, h, moves)
        beta = min(beta, value)

        if beta <= alpha:
            break

        if value < best_value:
            best = (x, y)
            best_value = value

    return best, best_value
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#----------------------------------------------------------------------INTERMEDIATE AGENT-------------------------------------------------------------------------------------------------------#
def intermediateAgent(game, player):
    return minimaxAB(game, player, 3, utility1, moves)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#-------------------------------------------------------------------------EXPERT AGENT----------------------------------------------------------------------------------------------------------#
def ExpertAgent(game, player):
    return minimaxAB(game, player, 3, utility2, moves)
#-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#
def moves(game, player):
    for x in range(game.size):
        for y in range(game.size):
            if game[x, y] == EMPTY:
                yield (x, y)

#----------------------------------------------------------------------------UTILITY FUNCTIONS-------------------------------------------------------------------------------------------------#
def utility1(game, player):

    val = 0
    global FLAG
    
    if player == 'R':
        opponent = 'B'
    
    else:
        opponent = 'R'

    c1 = cnnc2(game, player)
    c2 = cnnc2(game, opponent)

    for x, y in moves(game, opponent):
        clone = game.clone_play(x, y)
        if clone.winner() == opponent:
            return -200

    for x, y in moves(game, player):
        clone = game.clone_play(x, y)
        if clone.winner() == player:
            return 200

    connected_direction_weight = 2
    connected_direction = 0

    if player == 'B':
        # Checking for connected paths from left to right
        for i in range(game.size):
            if game[0, i] == player:
                connected_direction += 1

    elif player == 'R':
        # Checking for connected paths from top to bottom
        for i in range(game.size):
            if game[i, 0] == player:
                connected_direction += 1

    val += connected_direction_weight * connected_direction

    if game.board[0][0] == player and game.board[0][1] != opponent:
        val = -200
        FLAG += 1

    return ((c2 - c1) / max(c1, c2)) + val


def utility2(game, player):
    val = 0
    
    if player == 'R':
        opponent = 'B' 
    
    else:
        opponent = 'R'

    c1 = cnnc1(game, player)
    c2 = cnnc1(game, opponent)

    #if game.board[0][0] == player and game.board[0][1] != opponent:
        #val = -200
        
    score = ((c2 - c1) / max(c1, c2))
    return score


def getNeighbors(game, player, x, y):
    neighbors_blue = [(-1, 1), (0, 1), (1, -1), (0, -1)]
    neighbors_red = [(1, -1), (1, 0), (-1, -1), (-1, 0)]
    neighborhood = []

    if player == 'B':
        neighborhood = neighbors_blue
    else:
        neighborhood = neighbors_red

    for n in neighborhood:
        n1, n2 = x + n[0], y + n[1]
        if game.checkInside(n1, n2):
            yield n1, n2

def cnnc1(game, player):
    counted = set()
    connected = 0

    for i in range(game.size):
        for j in range(game.size):
            if game[i, j] == player:
                neighbors = getNeighbors(game, player, i, j)
                for n in neighbors:
                    r, c = n
                    if game[i, j] == player and n not in counted:
                        counted.add((r, c))
                        connected += 1
    return connected


def cnnc2(game, player):
    counted = set()
    connected = 0

    for i in range(game.size):
        for j in range(game.size):
            if game[i, j] == player:
                neighbors = game.neighbour(i, j)
                for n in neighbors:
                    r, c = n
                    if game[i, j] == player and n not in counted:
                        counted.add((r, c))
                        connected += 1
    return connected

#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#

#------------------------------------------------------------------------------GAME LOGIC------------------------------------------------------------------------------------------------------#
def testGame(SIZE, mode, color):
    game = Game(SIZE)

    # Human vs Random Agent--- Easy mode
    if mode == 1:
        # If Human selects to play as BLUE
        if color.capitalize() == 'B':

            print(game)
            while game.winner() == EMPTY:
                if game.turn == 0:
                    print("Human PLayer will play!!")
                    print("Enter your Move as ROW <space> COLUMN :\n")
                    
                    try:
                        x, y = list(map(int, input().split()))
                    
                    except:
                        print("Need values for ROW and COLUMN")

                else:
                    print("Agent will play!!")
                    x, y = randomAgent(game)

                try:
                    game.play(x, y)

                except GameError as e:
                    print(e)
                print(game)
                print(Style.RESET_ALL)
            print("WINNER: ", game.winner())
            if game.winner() == 'B':
                print("\n Human Player Wins!!")
            else:
                print("\n Random Agent Wins!!")

        # If Human selects to play as RED
        if color.capitalize() == 'R':

            print(game)
            while game.winner() == EMPTY:
                if game.turn == 0:
                    print("Agent will play!!")

                    x, y = randomAgent(game)

                else:
                    print("Human will play!!")
                    print("Enter your Move as ROW <space> COLUMN :\n")
                    try:
                        x, y = list(map(int, input().split()))

                    except:
                        print("Need values for ROW and COLUMN")                    
                try:
                    game.play(x, y)

                except GameError as e:
                    print(e)
                print(game)
                print(Style.RESET_ALL)
            print("WINNER: ", game.winner())
            if game.winner() == 'R':
                print("\n Human Player Wins!!")
            else:
                print("\n Random Agent Wins!!")

    # Human vs Medium Difficulty Agent
    
    # Random Agent vs Medium Difficulty Agent
    if mode == 2:
        print(game)
        while game.winner() == EMPTY:
            if game.turn == 0:
                print("Random Agent will play!!")

            else:
                print("Intermediate Agent will play!!")

            try:
                if game.turn == 0:
                    x, y = randomAgent(game)
                    game.play(x, y)

                else:
                    move = intermediateAgent(game.__clone__(), game.current())
                    game.play(*move)

            except GameError as e:
                print(e)

            print(game)
            print(Style.RESET_ALL)
        print("WINNER: ", game.winner())
        if game.winner() == 'R':
            print("\n Intermediate Agent Wins!!")
        else:
            print("\n Random Agent Wins!!")

    if mode == 3:
        print(game)
        while game.winner() == EMPTY:
            if game.turn == 0:
                print("Random Agent will play!!")

            else:
                print("Expert Agent will play!!")

            try:
                if game.turn == 0:
                    x, y = randomAgent(game)
                    game.play(x, y)

                else:
                    move = ExpertAgent(game.__clone__(), game.current())
                    game.play(*move)

            except GameError as e:
                print(e)

            print(game)
            print(Style.RESET_ALL)
        print("WINNER: ", game.winner())
        if game.winner() == 'R':
            print("\n Expert Agent Wins!!")
        else:
            print("\n Random Agent Wins!!")

    # Medium Difficulty Agent vs Hard Difficulty Agent
    if mode == 4:
        print(game)
        while game.winner() == EMPTY:
            if game.turn == 0:
                print("Intermediate Agent will play!!")

            else:
                print("Expert Agent will play!!")

            try:
                if game.turn == 0:
                    move = intermediateAgent(game.__clone__(), game.current())
                    game.play(*move)

                else:
                    move = ExpertAgent(game.__clone__(), game.current())
                    game.play(*move)

            except GameError as e:
                print(e)

            print(game)
            print(Style.RESET_ALL)
        print("WINNER: ", game.winner())
        if game.winner() == 'R':
            print("\n Expert Agent Wins!!")
        else:
            print("\n Intermediate Agent Wins!!")


#-----------------------------------------------------------------------------------MAIN-------------------------------------------------------------------------------------------------------#
def main():
    SIZE = int(input("Enter Board Size (Default = 5, MIN = 2): \n"))
    if SIZE == 1:
        exit("\nTold you")
    mode = int(
        input("1:Human vs RandomAgent \t 2: RandomAgent vs IntermediateAgent \t 3: RandomAgent vs ExpertAgent \t 4: IntermediateAgent vs ExpertAgent\n"))
    if mode == 1:
        color = input("Which Color Do You Want To Play As \n B: Blue \n R: Red\n")
        if color.capitalize() != 'B' and color.capitalize() != 'R':
            exit("Wrong Color Entered")
        testGame(SIZE, mode, color)

    if mode == 2:
        testGame(SIZE, mode, None)

    if mode == 3:
        testGame(SIZE, mode, None)

    if mode == 4:
        testGame(SIZE, mode, None)


if __name__ == '__main__':
    main()
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------#