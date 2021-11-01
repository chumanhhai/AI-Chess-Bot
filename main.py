import copy

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
board_colors = [p.Color(255, 206, 158), p.Color(209, 139, 71)]
marked_color = p.Color(170, 162, 59)


def load_images():
    pieces = ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR", "bP", "wP",
              "wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
    for piece in pieces:
        image = p.image.load("images/" + piece + ".png")
        images[piece] = image


def load_screen():
    p.init()
    p.display.set_caption("chess")
    p.display.set_icon(p.image.load("images/icon1.png"))
    gs = engine.GameState()
    load_images()
    draw_screen(gs)
    run(gs)


def draw_control_elements(gs):
    # header image
    image = p.image.load("images/chess_header.png")
    image = p.transform.scale(image, (150, 75))
    screen.blit(image, p.Rect(BOARD_WIDTH + 25, 50, 0, 0))

    # btn reset
    btn_undo = Button.Button(screen, (BOARD_WIDTH + 75, 400), "Undo", 24, "black on white")
    btn_undo.command = lambda: did_tap_reset_btn(gs)
    btn_undo.draw_button1()

    # state
    if gs.ending:
        draw_status_text(gs.result)


def draw_status_text(status):
    font = p.font.SysFont("Arial", 28, True, False)
    text = font.render(status, 0, p.Color("gray"))
    location = p.Rect(BOARD_WIDTH + (STATE_WIDTH-text.get_width())/2, 200, 0, 0)
    screen.blit(text, location)

    text = font.render(status, 0, p.Color("white"))
    location = location.move(-2, -2)
    screen.blit(text, location)


def did_tap_reset_btn(gs):
    gs.undo_move()
    gs.undo_move()


def run(gs):
    clock = p.time.Clock()
    running = True
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            if e.type == p.MOUSEBUTTONDOWN and not gs.ending:
                location = p.mouse.get_pos()
                row = int(location[1] // SQ_SIZE)
                col = int(location[0] // SQ_SIZE)
                if row >= DIMENSION or col >= DIMENSION: # if not click on board
                    continue
                if gs.whiteToMove and not gs.clickBuffer: # if the first click
                    piece = gs.board[row][col]
                    if piece == '--' or piece[0] == 'b':
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
                        animate_move(gs, clock)
                        if not gs.whiteToMove and not gs.ending: # bot turn
                            move, score = gs.minimax(0, -gs.INFINITY, gs.INFINITY)
                            if score == -gs.checkmate_score: # to optimize checkmate
                                gs.depth = 1
                            print("MAX SCORE: ", score)
                            gs.make_move(move)
                            animate_move(gs, clock)
                    continue
        Button.buttons.update()
        clock.tick(MAX_FPS)
        draw_screen(gs)
        p.display.flip()


def draw_state(gs):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            idx = (r + c) % 2
            color = board_colors[idx]
            piece = gs.board[r][c]
            if (r, c) == gs.clickBuffer:
                p.draw.rect(screen, marked_color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            else:
                p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if piece != "--":
                screen.blit(images[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, 0, 0))


def draw_screen(gs):
    screen.fill(p.Color("black"))
    draw_state(gs)
    draw_control_elements(gs)


def animate_move(gs, clock):
    move = gs.moveLog[-1]
    FPS = 40
    (start_r, start_c) = move.start_pos
    (end_r, end_c) = move.end_pos
    dR = end_r - start_r
    dC = end_c - start_c
    for frame in range(FPS+1):
        tem_r = start_r + dR*frame/FPS
        tem_c = start_c + dC*frame/FPS
        draw_state(gs)
        # re-draw start piece and end piece
        p.draw.rect(screen, board_colors[(start_r+start_c)%2],
                    p.Rect(start_c*SQ_SIZE, start_r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        if move.end_piece != '--':
            p.draw.rect(screen, board_colors[(end_r + end_c) % 2],
                        p.Rect(end_c * SQ_SIZE, end_r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            screen.blit(images[move.end_piece], p.Rect(end_c * SQ_SIZE, end_r * SQ_SIZE, 0, 0))
        else:
            p.draw.rect(screen, board_colors[(end_r + end_c) % 2],
                        p.Rect(end_c * SQ_SIZE, end_r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        # draw animation
        screen.blit(images[move.start_piece], p.Rect(tem_c * SQ_SIZE, tem_r * SQ_SIZE, 0, 0))
        clock.tick(MAX_FPS)
        p.display.flip()
    draw_state(gs)
    p.display.flip()


if __name__ == "__main__":
    load_screen()
