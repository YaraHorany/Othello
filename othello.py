import pygame  
import copy
import random
from constants import *

FPS = 60

pygame.init()
pygame.display.set_caption("Othello")
win = pygame.display.set_mode([WIDTH,HEIGHT])

# --- CLASSES ---

class Game:
    def __init__(self):
        self.board = Board()
        self.ai = AI()
        self.mode = 'ai' # ai OR pvp
        self.turn = BLACK # Black always moves first
        self.white_tiles = 2
        self.black_tiles = 2
        self.empty_spaces = ROWS * COLS - 4
        self.valid_moves = []
        self.directions = []
        self.show_score()

    def update(self):
        self.valid_moves, self.directions = self.board.get_valid_moves(self.turn)
        winner = self.winner()

        # if there's a winner then show the winner on the screen and end the game.
        if winner != None:
            self.show_winner(winner)

        # A player without a move simply passes, and the other player keeps playing pieces until the first player can make a move again.
        elif self.has_no_moves():
            self.change_turn()
            self.show_score()

        self.board.draw()
        pygame.display.update()

    # update the number of black tiles and white tiles
    def update_score(self, flipped_pieces):
        # In each round the number of empty spaces decreases by one
        self.empty_spaces -= 1

        # flipped pieces are the tiles which changed their colore
        if self.turn == BLACK:
            self.black_tiles += 1
            self.black_tiles += flipped_pieces
            self.white_tiles -= flipped_pieces
        else:
            self.white_tiles += 1
            self.white_tiles += flipped_pieces
            self.black_tiles -= flipped_pieces

    # when the game is finished, show who's the winner on the screen
    def show_winner(self, winner):
        pygame.draw.rect(win, BACKGROUND_COLOR, (0, 0, WIDTH, 100)) # delete previous score
        font1 = pygame.font.Font('freesansbold.ttf', 25)
        win.blit(font1.render(f"Game finished - {winner} won", True, BLACK), (120, 40))

    # show score on screen
    def show_score(self):
        pygame.draw.rect(win, BACKGROUND_COLOR, (0, 0, WIDTH, 100)) # delete previous score

        pygame.draw.circle(win, WHITE, [100, 50], 20, 0) 
        pygame.draw.circle(win, BLACK, [475, 50], 20, 0) 

        font = pygame.font.Font('freesansbold.ttf', 25)
        win.blit(font.render(f"{self.white_tiles}", True, BLACK), (150, 40))
        win.blit(font.render(f"{self.black_tiles}", True, BLACK), (525, 40))

        # show who's turn is now
        if self.turn == BLACK:
            win.blit(font.render(f"Turn: BLACK", True, BLACK), (220, 40))
        else:
            win.blit(font.render(f"Turn: WHITE", True, WHITE), (220, 40))

    # check if it's a valid move for the player then update board
    def select(self, row, col):
        flipped_pieces = 0
        if (row, col) in self.valid_moves:
            for direction in self.directions[self.valid_moves.index((row, col))]:
                flipped_pieces += self.board.pieces_to_flip(row, col, direction, self.turn)
            self.board.update_square(row, col, self.turn)
            self.update_score(flipped_pieces)
            self.change_turn()
            self.show_score()

    # swich turns
    def change_turn(self):
        self.valid_moves = []
        self.directions = []
        if self.turn == BLACK:
            self.turn = WHITE
        else:
            self.turn = BLACK

    # return true if there's no optional moves this round
    def has_no_moves(self):
        return len(self.valid_moves) == 0

    # check if there's a winner and return BLACK or WHITE. if there's no winner yet return None
    def winner(self):
        if self.white_tiles == 0:
            return 'BLACK'
        elif self.black_tiles == 0:
            return 'WHITE'
        elif (len(self.board.get_valid_moves(BLACK)) == 0 and len(self.board.get_valid_moves(WHITE)) == 0) or self.empty_spaces == 0:
            if self.white_tiles > self.black_tiles:
                return 'WHITE'
            elif self.black_tiles > self.white_tiles:
                return 'BLACK'

    # restart game
    def reset(self):
        self.__init__()

    # pvp - player versus player
    # ai - play agaist computer
    def change_gamemode(self):
        self.mode = 'ai' if self.mode == 'pvp' else 'pvp'

class Board:
    def __init__(self):
        self.board = []
        self.draw_lines()
        self.create_board()

    # draw board
    def draw_lines(self):
        win.fill(BACKGROUND_COLOR)
        for row in range(ROWS + 1):
            pygame.draw.line(win, BLACK, (0, 100 + (row * 75)),(600, 100 + (row * 75)))
            pygame.draw.line(win, BLACK, (row * 75, 100),(row * 75, 700))

    # The starting Othello board has two white tiles and two black tiles.
    def create_board(self):
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                # The four squares in the middle of the board start with four tiles already placed:
                # white top left and bottom right; black top right and bottom left
                if row == 3 and col == 3:
                    self.board[row].append(Tile(row, col, WHITE))
                elif row == 3 and col == 4:
                    self.board[row].append(Tile(row, col, BLACK))
                elif row == 4 and col == 3:
                    self.board[row].append(Tile(row, col, BLACK))
                elif row == 4 and col == 4:
                    self.board[row].append(Tile(row, col, WHITE))
                else:
                    self.board[row].append(0) # empty squares

    # draw tiles on screen
    def draw(self):
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.board[row][col]
                if tile != 0: # if tile exists then draw specefic tile
                    tile.draw(win) 

    def get_tile(self, row, col):
        return self.board[row][col]

    # The function returns a tuple with the directions if exists.
    def is_possible_move_by_empty_squares(self, row, col, turn):
        directions = []

        other = self.other_tile(turn)

        # east
        count = 0
        j = col + 1
        if j < COLS:
            tile = self.get_tile(row, j)
        while j < COLS and tile != 0 and tile.color == other:
            count += 1
            j += 1
            if j < COLS:
                tile = self.get_tile(row, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("east")

        # west
        count = 0
        j = col - 1
        if j >= 0:
            tile = self.get_tile(row, j)
        while j >= 0 and tile != 0 and tile.color == other:
            count += 1
            j -= 1
            if j >= 0:
                tile = self.get_tile(row, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("west")

        # north
        count = 0
        i = row - 1
        if i >= 0:  
            tile = self.get_tile(i, col)
        while i >= 0 and tile != 0 and tile.color == other:
            count += 1
            i -= 1
            if i >= 0:
                tile = self.get_tile(i, col)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("north")

        # south
        count = 0
        i = row + 1
        if i < ROWS:
            tile = self.get_tile(i, col)
        while i < ROWS and tile != 0 and tile.color == other:
            count += 1
            i += 1
            if i < ROWS:
                tile = self.get_tile(i, col)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("south")

        # northeast
        count = 0
        i = row - 1
        j = col + 1
        if i >= 0 and j < COLS:
            tile = self.get_tile(i, j)
        while i >= 0 and j < COLS and tile != 0 and tile.color == other:
            count += 1
            i -= 1
            j += 1
            if i >= 0 and j < COLS:
                tile = self.get_tile(i, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("northeast")

        # northwest
        count = 0
        i = row - 1
        j = col - 1
        if i >= 0 and j >= 0:
            tile = self.get_tile(i, j)
        while i >= 0 and j >= 0 and tile != 0 and tile.color == other:
            count += 1
            i -= 1
            j -= 1
            if i >= 0 and j >= 0:
                tile = self.get_tile(i, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("northwest")

        # southeast
        count = 0
        i = row + 1
        j = col + 1
        if i < ROWS and j < COLS:
            tile = self.get_tile(i, j)
        while i < ROWS and j < COLS and tile != 0 and tile.color == other:
            count += 1
            i += 1
            j += 1
            if i < ROWS and j < COLS:
                tile = self.get_tile(i, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("southeast")

        # southwest
        count = 0
        i = row + 1
        j = col - 1
        if i < ROWS and j >= 0:
            tile = self.get_tile(i, j)
        while i < ROWS and j >= 0 and tile != 0 and tile.color == other:
            count += 1
            i += 1
            j -= 1
            if i < ROWS and j >= 0:
                tile = self.get_tile(i, j)
        if count > 0 and tile !=0 and tile.color == turn:
            directions.append("southwest")

        tuple_directions = tuple(directions)

        return tuple_directions

    # get the valid move for the current player
    def get_valid_moves(self, turn):
        valid_moves = []
        directions = []
        for row in range(ROWS):
            for col in range(COLS):
                tile = self.get_tile(row, col)
                if tile == 0:
                    tuple_directions = self.is_possible_move_by_empty_squares(row, col, turn)
                    if len(tuple_directions) != 0:
                        valid_moves.append((row, col))
                        directions.append(tuple_directions)
        return valid_moves, directions

    def pieces_to_flip(self, row, col, direction, turn):
        if direction == 'east':
            flipped_pieces = self.flip_row(row, col + 1, direction, turn)
        elif direction == 'west':
            flipped_pieces = self.flip_row(row, col - 1, direction, turn)
        elif direction == 'north':
            flipped_pieces = self.flip_row(row - 1, col, direction, turn)
        elif direction == 'south':
            flipped_pieces = self.flip_row(row + 1, col, direction, turn)
        elif direction == 'northeast':
            flipped_pieces = self.flip_row(row - 1, col + 1, direction, turn)
        elif direction == 'northwest':
            flipped_pieces = self.flip_row(row - 1, col - 1, direction, turn)
        elif direction == 'southeast':
            flipped_pieces = self.flip_row(row + 1, col + 1, direction, turn)
        elif direction == 'southwest':
            flipped_pieces = self.flip_row(row + 1, col - 1, direction, turn)
        return flipped_pieces

    # flip all tiles in the whole row depending on the giving direction
    def flip_row(self, row, col, direction, turn):
        flipped_pieces = 0
        other = self.other_tile(turn)
        tile = self.get_tile(row, col)
        while tile.color == other:
            tile.change_color()
            flipped_pieces += 1
            if direction == 'east' or direction == 'northeast' or direction == 'southeast':
                col += 1
            if direction == 'west' or direction == 'northwest' or direction == 'southwest':
                col -= 1
            if direction == 'south' or direction == 'southeast' or direction == 'southwest':
                row += 1
            if direction == 'north' or direction == 'northeast' or direction == 'northwest':
                row -= 1
            tile = self.get_tile(row, col)
        return flipped_pieces

    # Put a tile on the empty square
    def update_square(self, row, col, color):
        self.board[row][col] = Tile(row, col, color)

    # returns the other tile
    def other_tile(self, turn):
        if turn == WHITE:
            other_tile = BLACK
        else:
            other_tile = WHITE
        return other_tile

class Tile:
    def __init__(self, row, col, color):
        self.row = row
        self.col = col
        self.color = color        
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = (SQUARE_SIZE * self.row + SQUARE_SIZE // 2) + 100

    def draw(self, win):
        pygame.draw.circle(win, self.color, [self.x, self.y], 20, 0) # x and y are the center of the circle, 20 is the radius

    # flip tile and change it's color
    def change_color(self):
        if self.color == BLACK:
            self.color = WHITE
        else:
            self.color = BLACK

class AI:
    def __init__(self, level = 1):
        self.level = level

    def rand_move(self, game):
        # the AI player plays with white tiles
        if game.turn == BLACK:
            return None

        game.valid_moves, game.directions = game.board.get_valid_moves(WHITE)
        if len(game.valid_moves) == 0:
            game.change_turn()
            return None

        idx = random.randrange(0, len(game.valid_moves))
        return game.valid_moves[idx] # (row, col)

    # Returns the optimal action for the ai player on the game.
    def minimax(self, game, depth, maximizing, alpha, beta):
        winner = game.winner()

        if depth == 0:
            if game.black_tiles > game.white_tiles:
                return 1, None # eval, move
            elif game.white_tiles > game.black_tiles:
                return -1, None # eval, move
            else:
                return 0, None

        if maximizing:
            game.turn = BLACK
            game.valid_moves, game.directions = game.board.get_valid_moves(BLACK)
        if not maximizing:
            game.turn = WHITE
            game.valid_moves, game.directions = game.board.get_valid_moves(WHITE)

        if game.has_no_moves() and winner == None:
            game.change_turn()
            maximizing = not maximizing
            if maximizing:
                game.valid_moves, game.directions = game.board.get_valid_moves(BLACK)
            if not maximizing:
                game.valid_moves, game.directions = game.board.get_valid_moves(WHITE)

        if winner == 'BLACK':
            return 1, None # eval, move
        elif winner == 'WHITE':
            return -1, None # eval, move    

        if maximizing:
            max_eval = float("-inf")
            best_move = None
            for (row, col) in game.valid_moves:
                temp_game = copy.deepcopy(game)
                flipped_pieces = 0
                for direction in temp_game.directions[temp_game.valid_moves.index((row, col))]:
                    flipped_pieces += temp_game.board.pieces_to_flip(row, col, direction, BLACK) 
                temp_game.board.update_square(row, col, BLACK)
                temp_game.update_score(flipped_pieces)

                eval = self.minimax(temp_game, depth - 1, False, alpha, beta)[0]

                if eval > max_eval:
                    max_eval = eval
                    best_move = (row, col)
                alpha = max(alpha, max_eval)
                if beta <= alpha:
                    return 1, best_move # break 

            return max_eval, best_move

        elif not maximizing:
            min_val = float("inf")
            best_move = None
            for (row, col) in game.valid_moves:
                temp_game = copy.deepcopy(game)
                flipped_pieces = 0
                for direction in temp_game.directions[temp_game.valid_moves.index((row, col))]:
                    flipped_pieces += temp_game.board.pieces_to_flip(row, col, direction, WHITE)
                temp_game.board.update_square(row, col, WHITE)
                temp_game.update_score(flipped_pieces)

                eval = self.minimax(temp_game, depth - 1, True, alpha, beta)[0]

                if eval < min_val:
                    min_val = eval
                    best_move = (row, col)
                beta = min(beta, min_val)
                if beta <= alpha:
                    return 1, best_move # break 

            return min_val, best_move

    def eval(self, main_game):

        if self.level == 0:
            # Playing with a random AI
            move = self.rand_move(main_game)
        else: 
            # Run the minimax algorithm. maximum depth is 5
            eval, move = self.minimax(main_game, 5, False, float("-inf") ,float("inf"))

        return move # row, col

def get_row_col_from_mouse(pos):
    x, y = pos
    row = (y - 100) // SQUARE_SIZE
    col = x // SQUARE_SIZE
    if row >= 0:
        return row, col
    else: 
        return None

if __name__ == '__main__':

    running = True # Run until the user asks to quit

    clock = pygame.time.Clock()
    game = Game()
    board = game.board
    ai = game.ai

    while running:
        clock.tick(FPS)

        for event in pygame.event.get():

            # quit event
            if event.type == pygame.QUIT:
                running = False

            # keydown event
            if event.type == pygame.KEYDOWN:

                # g-gamemode
                if event.key == pygame.K_g:
                    game.change_gamemode()

                # r-restart
                if event.key == pygame.K_r:
                    game.reset()
                                
                # 0-random ai               
                if event.key == pygame.K_0:
                    ai.level = 0
                
                # 1-minimax algorithm
                if event.key == pygame.K_1:
                    ai.level = 1

            # click event
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                pos = get_row_col_from_mouse(pos)
                if pos != None:
                    row, col = pos
                    game.select(row, col)

            elif game.mode == 'ai' and game.turn == WHITE:
                returned_eval = ai.eval(game)
                if returned_eval != None:
                    row, col = returned_eval
                    game.select(row, col)

        game.update()
  
    pygame.quit()