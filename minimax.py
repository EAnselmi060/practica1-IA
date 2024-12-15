import pygame
import sys
import math
import copy

# Inicializar pygame
pygame.init()

# Dimensiones de la ventana y los colores
WIDTH, HEIGHT = 400, 400
ROWS, COLS = 4, 4
SQUARE_SIZE = WIDTH // COLS

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)

# Crear ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tablero de Damas 4x4")

# Estado del tablero
board = [[None for _ in range(COLS)] for _ in range(ROWS)]
selected_piece = None
current_turn = "black"  # Turno inicial (agente)
moves_without_capture = 0

# Inicializar piezas
for col in range(0, COLS, 2):
    board[0][col] = "black"
    board[3][col + 1] = "white"

def is_queen(piece, row):
    return (piece == "white" and row == 0) or (piece == "black" and row == ROWS - 1)

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = BLACK if (row + col) % 2 == 0 else WHITE
            pygame.draw.rect(screen, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    radius = SQUARE_SIZE // 3
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            if piece == "black":
                pygame.draw.circle(screen, BLACK, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius)
                pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius, 2)
            elif piece == "white":
                pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius)
            elif piece == "BLACK":  # Reina negra
                pygame.draw.circle(screen, BLACK, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius)
                pygame.draw.circle(screen, GOLD, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius, 2)
            elif piece == "WHITE":  # Reina blanca
                pygame.draw.circle(screen, WHITE, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius)
                pygame.draw.circle(screen, GOLD, (col * SQUARE_SIZE + SQUARE_SIZE // 2, row * SQUARE_SIZE + SQUARE_SIZE // 2), radius, 2)
                
def get_square_under_mouse():
    mouse_x, mouse_y = pygame.mouse.get_pos()
    col = mouse_x // SQUARE_SIZE
    row = mouse_y // SQUARE_SIZE
    return row, col

def is_within_bounds(row, col):
    return 0 <= row < ROWS and 0 <= col < COLS

def get_all_valid_moves(player):
    moves = []
    capture_moves = []

    for row in range(len(board)):
        for col in range(len(board[row])):
            if board[row][col] is not None and board[row][col].lower() == player.lower():
                new_moves, new_capture_moves = get_piece_moves(row, col)
                moves.extend(new_moves)
                capture_moves.extend(new_capture_moves)
                
    
    return capture_moves if capture_moves else moves

def is_valid_capture(piece_row, piece_col, target_row, target_col):
    
    if abs(target_row - piece_row) == 2:  # Movimiento de captura donde se dirige - donde esta actualmente
        middle_row = (piece_row + target_row) // 2
        middle_col = (piece_col + target_col) // 2

        if is_within_bounds(middle_row, middle_col) and is_within_bounds(target_row, target_col):
            # Verificar si la pieza en el medio o el objetivo está en el borde
            #if is_at_edge(middle_row, middle_col): #or is_at_edge(target_row, target_col):
            #    return False
            
            # Verificar que la casilla donde caerá la ficha esté vacía
            if board[target_row][target_col] is not None:
                return False


            return (
                board[middle_row][middle_col] is not None
                and board[middle_row][middle_col].lower() != board[piece_row][piece_col].lower()
            )
    return False

def is_at_edge(row, col):
    return row == 0 or row == ROWS - 1 or col == 0 or col == COLS - 1

def get_piece_moves(piece_row, piece_col):
    moves = []
    capture_moves = []

    piece = board[piece_row][piece_col]
    directions = []

    # Determinar direcciones permitidas
    if piece.lower() == "white":
        directions = [(-1, 1), (-1, -1)]  # Sólo moverse hacia arriba
    elif piece.lower() == "black":
        directions = [(1, 1), (1, -1)]  # Sólo moverse hacia abajo

    # Permitir movimientos en ambas direcciones para reinas
    if piece == "WHITE" or piece == "BLACK":
        directions = [
            (1, 1), (1, -1),  # Diagonales hacia abajo
            (-1, 1), (-1, -1)  # Diagonales hacia arriba
        ]

    for dr, dc in directions:
        # Movimiento normal (una casilla en la dirección)
        target_row, target_col = piece_row + dr, piece_col + dc
        if is_valid_move(piece_row, piece_col, target_row, target_col, capture=False):
            moves.append(((piece_row, piece_col), (target_row, target_col)))

        # Movimiento de captura (dos casillas en la dirección, debe capturar una pieza)
        capture_row, capture_col = piece_row + 2 * dr, piece_col + 2 * dc
        if is_valid_capture(piece_row, piece_col, capture_row, capture_col):
            # Verificar si la captura lleva la pieza al borde del tablero
            #if not is_at_edge(capture_row, capture_col):
            capture_moves.append(((piece_row, piece_col), (capture_row, capture_col)))

    #print("--movimientos de captura---")
    #print(capture_moves)
    
        
    return moves, capture_moves

def is_valid_move(piece_row, piece_col, target_row, target_col, capture=True):
    if not is_within_bounds(target_row, target_col):
        return False

    piece = board[piece_row][piece_col]
    if piece is None:
        return False

    direction = -1 if piece.lower() == "white" else 1

    # Movimiento diagonal básico
    if abs(target_row - piece_row) == 1 and abs(target_col - piece_col) == 1:
        if piece == "white" and target_row > piece_row:
            return False
        
        if board[target_row][target_col] is None:
            return True

    # Comer una pieza
    if capture and abs(target_row - piece_row) == 2 and abs(target_col - piece_col) == 2:
        middle_row = (piece_row + target_row) // 2
        middle_col = (piece_col + target_col) // 2
        if (
            is_within_bounds(middle_row, middle_col)
            and board[middle_row][middle_col] is not None
            and board[middle_row][middle_col].lower() != piece.lower()
        ):
            return True

    return False

def make_move(piece_row, piece_col, target_row, target_col):
    global moves_without_capture

    piece = board[piece_row][piece_col]
    board[piece_row][piece_col] = None
    board[target_row][target_col] = piece.upper() if is_queen(piece, target_row) else piece

    if abs(target_row - piece_row) == 2:
        middle_row = (piece_row + target_row) // 2
        middle_col = (piece_col + target_col) // 2
        board[middle_row][middle_col] = None
        moves_without_capture = 0
    else:
        moves_without_capture += 1


def animate_move(piece_row, piece_col, target_row, target_col):
    piece = board[piece_row][piece_col]
    start_x = piece_col * SQUARE_SIZE + SQUARE_SIZE // 2
    start_y = piece_row * SQUARE_SIZE + SQUARE_SIZE // 2
    end_x = target_col * SQUARE_SIZE + SQUARE_SIZE // 2
    end_y = target_row * SQUARE_SIZE + SQUARE_SIZE // 2

    frames = 15
    for frame in range(frames):
        t = frame / (frames - 1)
        current_x = start_x + t * (end_x - start_x)
        current_y = start_y + t * (end_y - start_y)

        draw_board()
        draw_pieces()
        pygame.draw.circle(screen, BLACK if piece.lower() == "black" else WHITE, (int(current_x), int(current_y)), SQUARE_SIZE // 3)
        pygame.display.flip()
        pygame.time.delay(30)

def is_terminal(): #funcion fin del juego
    if moves_without_capture >= 64:
        return True, 0  # Empate

    white_exists = any(cell == "white" or cell == "WHITE" for row in board for cell in row)
    black_exists = any(cell == "black" or cell == "BLACK" for row in board for cell in row)

    if not white_exists:
        return True, 1  # Gana el agente
    if not black_exists:
        return True, -1  # Pierde el agente

    return False, None

def heuristic():
    white_pieces = sum(cell == "white" or cell == "WHITE" for row in board for cell in row)
    black_pieces = sum(cell == "black" or cell == "BLACK" for row in board for cell in row)
    white_positions = sum(position_value(row, col, "white") for row in range(len(board)) for col in range(len(board[0])))
    black_positions = sum(position_value(row, col, "black") for row in range(len(board)) for col in range(len(board[0])))
    return (black_pieces - white_pieces) + (black_positions - white_positions)

def position_value(row, col, color):
    center_bonus = 1 if (row, col) in [(1, 1), (1, 2), (2, 1), (2, 2)] else 0
    value = center_bonus
    if color == "white":
        value += row
    else:
        value += (len(board) - 1 - row)
    return value

def minimax(depth, alpha, beta, maximizing):
    terminal, score = is_terminal()
    if terminal or depth == 0:
        return heuristic() if not terminal else score, None

    best_move = None
    if maximizing:
        max_eval = -math.inf
        print("--movimientos black--")
        for move in get_all_valid_moves("black"):
            temp_board = copy.deepcopy(board)
            make_move(*move[0], *move[1])
            eval, _ = minimax(depth - 1, alpha, beta, False)
            board[:] = temp_board
            
            print("--evaluacion--")
            print(f"{move},{eval}")

            if eval > max_eval:
                max_eval = eval
                best_move = move
            alpha = max(alpha, eval)
            if beta <= alpha:   #condicion de poda
                break
            
        
        return max_eval, best_move
    else:
        min_eval = math.inf
        print("--movimientos white--")
        for move in get_all_valid_moves("white"):
            temp_board = copy.deepcopy(board)
            make_move(*move[0], *move[1])
            eval, _ = minimax(depth - 1, alpha, beta, True)
            board[:] = temp_board

            if eval < min_eval:
                min_eval = eval
                best_move = move
            beta = min(beta, eval)
            if beta <= alpha:   #condicion de poda
                break
        return min_eval, best_move

def agent_move():
    _, best_move = minimax(5, -math.inf, math.inf, True)
    if best_move:
        print("--best de movimientos---")
        print(best_move)
        
        piece_row, piece_col = best_move[0]
        target_row, target_col = best_move[1]
        animate_move(piece_row, piece_col, target_row, target_col)
        make_move(piece_row, piece_col, target_row, target_col)

def main():
    global selected_piece, current_turn
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if current_turn == "white" and event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse()
                if selected_piece:
                    piece_row, piece_col = selected_piece
                    if board[row][col] is None and is_valid_move(piece_row, piece_col, row, col):
                        make_move(piece_row, piece_col, row, col)
                        selected_piece = None
                        current_turn = "black"
                    else:
                        selected_piece = None
                else:
                    if board[row][col] is not None and board[row][col].lower() == "white":
                        selected_piece = (row, col)

        if current_turn == "black":
            agent_move()
            current_turn = "white"

        draw_board()
        draw_pieces()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
