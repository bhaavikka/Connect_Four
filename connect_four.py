import pygame
import numpy as np
import math
import sys

# Constants
ROW_COUNT = 6 #numbers of rows in the connect four board
COLUMN_COUNT = 7 #number of columns in the connect four board
SQUARE_SIZE = 100 #size of each square in the grid
RADIUS = int(SQUARE_SIZE / 2 - 5) #radius of the circle representing a piece

#colours for the board and pieces
BLUE = (0, 0, 255) #board color
BLACK = (0, 0, 0) #background color
RED = (255, 0, 0) #player's piece color
YELLOW = (255, 255, 0) #AI's piece color

PLAYER = 0 #human player
AI = 1 #AI player

EMPTY = 0 #empty cell value
PLAYER_PIECE = 1 #player's piece value
AI_PIECE = 2 #AI's piece value

#WIN condition
WINDOW_LENGTH = 4 #the number of pieces in a row which is needed to win 

# Initialize pygame
pygame.init()
width = COLUMN_COUNT * SQUARE_SIZE
height = (ROW_COUNT + 1) * SQUARE_SIZE  # Extra row for player input
size = (width, height)
screen = pygame.display.set_mode(size)
font = pygame.font.SysFont("monospace", 75)


def create_board():
    """Initialize the board as a 2D array filled with zeros."""
    return np.zeros((ROW_COUNT, COLUMN_COUNT))


def is_valid_location(board, col):
    #Check if the top row of a column is empty, meaning the column can accept a piece.
    return board[ROW_COUNT - 1][col] == EMPTY


def get_next_open_row(board, col):
    #Find the next available row in a column for placing a piece.
    for r in range(ROW_COUNT):
        if board[r][col] == EMPTY:
            return r


def drop_piece(board, row, col, piece):
    #Place the piece in the specified row and column.
    board[row][col] = piece


def winning_move(board, piece):
    # Check horizontal location for win
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check vertical location for a win
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT):
            if all(board[r + i][c] == piece for i in range(WINDOW_LENGTH)):
                return True

#checking diagonals for a win (+ve slope, -ve slope)
    # Check positively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    # Check negatively sloped diagonal
    for r in range(3, ROW_COUNT):
        for c in range(COLUMN_COUNT - 3):
            if all(board[r - i][c + i] == piece for i in range(WINDOW_LENGTH)):
                return True

    return False


def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0


def score_position(board, piece):
    score = 0

    # Score center column
    center_array = [int(board[r][COLUMN_COUNT // 2]) for r in range(ROW_COUNT)]
    center_count = center_array.count(piece)
    score += center_count * 3

    # Score horizontal
    for r in range(ROW_COUNT):
        row_array = [int(board[r][c]) for c in range(COLUMN_COUNT)]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score vertical
    for c in range(COLUMN_COUNT):
        col_array = [int(board[r][c]) for r in range(ROW_COUNT)]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r + WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    # Score positively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    # Score negatively sloped diagonal
    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r + 3 - i][c + i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score


def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score


def get_valid_locations(board):
    return [col for col in range(COLUMN_COUNT) if is_valid_location(board, col)]

#MINMAX algorithm has been used 
def minimax(board, depth, alpha, beta, maximizingPlayer):
    #AI's decision making to find the best move 
    valid_locations = get_valid_locations(board) #get all valid columns
    is_terminal = is_terminal_node(board)#check if the game is over or not

    if depth == 0 or is_terminal:
        if is_terminal:#if terminal return a large +ve or -ve score
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:  # game is draw
                return (None, 0)
        else: #depth limit reached
            return (None, score_position(board, AI_PIECE))

#maximizing player(AI)
    if maximizingPlayer:
        value = -math.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, AI_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                best_col = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
#Minimizing player(Human)
    else:
        value = math.inf
        best_col = np.random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            temp_board = board.copy()
            drop_piece(temp_board, row, col, PLAYER_PIECE)
            new_score = minimax(temp_board, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                best_col = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return best_col, value


def draw_board(board):
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            pygame.draw.rect(screen, BLUE, (c * SQUARE_SIZE, r * SQUARE_SIZE + SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))
            pygame.draw.circle(screen, BLACK, (c * SQUARE_SIZE + SQUARE_SIZE // 2, r * SQUARE_SIZE + SQUARE_SIZE + SQUARE_SIZE // 2), RADIUS)

        for r in range(ROW_COUNT):
            for c in range(COLUMN_COUNT):
                if board[r][c] == PLAYER_PIECE:
                    pygame.draw.circle(screen, RED, (c * SQUARE_SIZE + SQUARE_SIZE // 2, height - (r * SQUARE_SIZE + SQUARE_SIZE // 2)), RADIUS)
                elif board[r][c] == AI_PIECE:
                    pygame.draw.circle(screen, YELLOW, (c * SQUARE_SIZE + SQUARE_SIZE // 2, height - (r * SQUARE_SIZE + SQUARE_SIZE // 2)), RADIUS)
    pygame.display.update()


# Main game loop
board = create_board()
game_over = False
turn = PLAYER

draw_board(board)
pygame.display.update()

while not game_over:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
#handle player input
        if event.type == pygame.MOUSEMOTION:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
            posx = event.pos[0]
            if turn == PLAYER:
                pygame.draw.circle(screen, RED, (posx, SQUARE_SIZE // 2), RADIUS)

        pygame.display.update()

        if event.type == pygame.MOUSEBUTTONDOWN:
            pygame.draw.rect(screen, BLACK, (0, 0, width, SQUARE_SIZE))
            if turn == PLAYER:
                posx = event.pos[0]
                col = posx // SQUARE_SIZE

                if is_valid_location(board, col):
                    row = get_next_open_row(board, col)
                    drop_piece(board, row, col, PLAYER_PIECE)

                    if winning_move(board, PLAYER_PIECE):
                        label = font.render("Player 1 wins!", 1, RED)
                        screen.blit(label, (40, 10))
                        game_over = True

                    turn += 1
                    turn = turn % 2

                    draw_board(board)

    # AI Turn
    if turn == AI and not game_over:
        col, minimax_score = minimax(board, 5, -math.inf, math.inf, True)

        if is_valid_location(board, col):
            pygame.time.wait(500)
            row = get_next_open_row(board, col)
            drop_piece(board, row, col, AI_PIECE)

            if winning_move(board, AI_PIECE):
                label = font.render("AI wins!", 1, YELLOW)
                screen.blit(label, (40, 10))
                game_over = True

            turn += 1
            turn = turn % 2

            draw_board(board)

    if game_over:
        pygame.time.wait(3000)
