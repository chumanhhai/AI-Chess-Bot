import pygame as p
import engine
import Button

HEIGHT = BOARD_WIDTH = 512
STATE_WIDTH = 200
WIDTH = BOARD_WIDTH + STATE_WIDTH
DIMENSION = 8
SQ_SIZE = HEIGHT / DIMENSION
MAX_FPS = 60
images = {}
screen = p.display.set_mode((WIDTH, HEIGHT))


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP", "wP",
              "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    for piece in pieces:
        image = p.image.load("images/" + piece + ".png")
        images[piece] = image


def load_screen():
    p.init()
    screen.fill(color=p.Color("black"))
    p.display.set_caption("chess")
    p.display.set_icon(p.image.load("images/icon1.png"))
    gs = engine.GameState()
    load_images()
    draw_control_elements(gs)
    draw_state(gs)
    run(gs)


def draw_control_elements(gs):
    # header
    image = p.image.load("images/chess_header.png")
    image = p.transform.scale(image, (150, 75))
    screen.blit(image, p.Rect(BOARD_WIDTH + 25, 50, 0, 0))

    # btn reset
    btn_undo = Button.Button(screen, (BOARD_WIDTH + 75, 400), "Undo", 24, "black on white")
    btn_undo.command = lambda: gs.undo_move()
    btn_undo.draw_button1()


def run(gs):
    clock = p.time.Clock()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN:
                location = p.mouse.get_pos()
                row = int(location[1] // SQ_SIZE)
                col = int(location[0] // SQ_SIZE)
                if row >= DIMENSION or col >= DIMENSION: # if not click on board
                    continue
                if not gs.clickBuffer: # if the first click
                    piece = gs.board[row][col]
                    if piece == '--':
                        continue
                    if (piece[0] == 'w' and not gs.whiteToMove) or (piece[0] == 'b' and gs.whiteToMove): # not in turn
                        continue
                    gs.clickBuffer = (row, col)
                else: # if the second click
                    if gs.clickBuffer == (row, col): # if click again
                        gs.clickBuffer = None
                        continue
                    if gs.is_ally(gs.board[row][col][0]): # if switch to another ally piece
                        gs.clickBuffer = (row, col)
                        continue
                    move = engine.Move(gs.clickBuffer, (row, col), gs.board)
                    if move in gs.valid_moves: # if valid move
                        gs.make_move(move)
        Button.buttons.update()
        clock.tick(MAX_FPS)
        draw_state(gs)
        p.display.flip()


def draw_state(gs):
    # colors = [p.Color("white"), p.Color("gray")]
    colors = [p.Color(255, 206, 158), p.Color(209, 139, 71)]
    # marked_color = p.Color("yellow")
    marked_color = p.Color(170, 162, 59)
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            idx = (r + c) % 2
            color = colors[idx]
            piece = gs.board[r][c]
            if (r, c) == gs.clickBuffer:
                p.draw.rect(screen, marked_color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if piece != "--":
                screen.blit(images[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, 0, 0))


if __name__ == "__main__":
    load_screen()
