import copy
import random


class GameState:
    INFINITY = 9999999

    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        # self.board = [["bR", "bN", "bB", "bQ", "bK", "wQ", "bN", "bR"],
        #               ["bP", "bP", "bP", "bP", "bP", "--", "bP", "bP"],
        #               ["--", "--", "--", "--", "--", "--", "--", "--"],
        #               ["--", "--", "--", "--", "--", "--", "--", "--"],
        #               ["--", "--", "--", "--", "--", "--", "--", "--"],
        #               ["--", "--", "--", "--", "--", "--", "--", "--"],
        #               ["wP", "wP", "wP", "wP", "wP", "wR", "wP", "wP"],
        #               ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.rank_score = {"wP": 10, "wN": 30, "wB": 30, "wR": 50, "wQ": 90, "wK": 10000,
                           "bP": -10, "bN": -30, "bB": -30, "bR": -50, "bQ": -90, "bK": -10000, "--": 0}
        self.checkmate_score = 10000
        self.state_score = 0
        self.result = ""
        self.whiteToMove = True
        self.ending = False
        self.moveLog = []
        self.clickBuffer = None
        self.bK_pos = (0, 4)
        self.wK_pos = (7, 4)
        self.check = False
        self.pinned = []
        self.depth = 3
        self.valid_moves = self.get_valid_moves()

    def random_move(self):
        if self.valid_moves:
            return random.choice(self.valid_moves)
        return None

    def minimax(self, depth, alpha, beta):
        if self.whiteToMove:
            if self.check and not self.valid_moves: # if checkmate
                return None, -self.checkmate_score
            if not self.check and not self.valid_moves: # if stalemate
                return None, 0
            if depth == self.depth: # terminate
                return None, self.state_score
            max_score = -self.INFINITY
            saved_moves = []
            valid_moves = copy.deepcopy(self.valid_moves)
            for move in valid_moves:
                self.make_move(move, True, False, True)
                _, score = self.minimax(depth+1, alpha, beta)
                self.undo_move(True, False)
                if max_score < score:
                    max_score = score
                    saved_moves = [move]
                elif max_score == score:
                    saved_moves.append(move)
                alpha = max(alpha, score)
                if alpha > beta:
                    break
            return random.choice(saved_moves), max_score
        else:
            if self.check and not self.valid_moves: # if checkmate
                return None, self.checkmate_score
            if not self.check and not self.valid_moves: # if stalemate
                return None, 0
            if depth == self.depth: # terminate
                return None, self.state_score
            min_score = self.INFINITY
            saved_moves = []
            priority_moves = []
            valid_moves = copy.deepcopy(self.valid_moves)
            for move in valid_moves:
                self.make_move(move, True, False, True)
                curr_score = self.state_score
                _, score = self.minimax(depth+1, alpha, beta)
                self.undo_move(True, False)
                if min_score > score:
                    min_score = score
                    saved_moves = [move]
                    if min_score == curr_score:
                        priority_moves = [move]
                    else:
                        priority_moves = []
                elif min_score == score:
                    saved_moves.append(move)
                    if min_score == curr_score:
                        priority_moves.append(move)
                beta = min(beta, score)
                if alpha > beta:
                    break
            if priority_moves:
                return random.choice(priority_moves), min_score
            else:
                return random.choice(saved_moves), min_score

    def switch_turn(self, real_move=True, should_get_moves=True):
        self.whiteToMove = not self.whiteToMove
        self.clickBuffer = None
        self.ending = False
        if should_get_moves:
            self.check, self.pinned = self.is_check()
            self.valid_moves = self.get_valid_moves()
        if real_move:
            print("current score: ", self.state_score)
            if self.check and not self.valid_moves:
                print("current state: checkmate")
                self.ending = True
                if self.whiteToMove:
                    self.result = "AI BOT Wins !"
                else:
                    self.result = "You Win !"
            if not self.check and not self.valid_moves:
                print("current state: stalemate")
                self.ending = True
                self.result = "Stalemate!"
            if self.check and self.valid_moves:
                print("current state: check")
                self.result = "Check !"
            if not self.check and self.valid_moves:
                print("current state: normal")
                self.result = ""
            print("===========================================")

    def make_move(self, move, is_switch_turn=True, real_move=True, should_get_moves=True):
        self.board[move.start_pos[0]][move.start_pos[1]] = '--'
        self.board[move.end_pos[0]][move.end_pos[1]] = move.start_piece
        # track the state score
        self.state_score -= self.rank_score[move.end_piece]
        # check if promotion
        if move.is_promotion:
            promoting_piece = move.start_piece[0] + 'Q'
            self.board[move.end_pos[0]][move.end_pos[1]] = promoting_piece
            # track the state score
            self.state_score -= self.rank_score[move.start_piece]
            self.state_score += self.rank_score[promoting_piece]
        # track the king pos
        if move.start_piece == 'wK':
            self.wK_pos = move.end_pos
        if move.start_piece == 'bK':
            self.bK_pos = move.end_pos
        self.moveLog.append(move)
        if is_switch_turn:
            if real_move:
                print(move.get_notation())
            self.switch_turn(real_move, should_get_moves)

    def undo_move(self, is_switch_turn=True, should_get_moves=True):
        if not self.moveLog: # assure there is already some moves
            return
        last_move = self.moveLog.pop()
        self.board[last_move.start_pos[0]][last_move.start_pos[1]] = last_move.start_piece
        self.board[last_move.end_pos[0]][last_move.end_pos[1]] = last_move.end_piece
        # track the state score
        self.state_score += self.rank_score[last_move.end_piece]
        # check if promotion
        if last_move.is_promotion:
            promoting_piece = last_move.start_piece[0] + 'Q'
            # track the state score
            self.state_score += self.rank_score[last_move.start_piece]
            self.state_score -= self.rank_score[promoting_piece]
        # track the king pos
        if last_move.start_piece == 'wK':
            self.wK_pos = last_move.start_pos
        if last_move.start_piece == 'bK':
            self.bK_pos = last_move.start_pos
        if is_switch_turn:
            if should_get_moves: # trigger when click on undo button
                self.depth = 3
            self.switch_turn(False, should_get_moves)

    def get_valid_moves(self):
        moves = []
        possible_moves = self.get_possible_moves()
        for move in possible_moves:
            if self.check: # if check
                self.make_move(move, False) # try to make move and check if still in check state
                check, _ = self.is_check()
                if not check:
                    moves.append(move)
                self.undo_move(False)
            else: # if not check
                if (move.start_pos in self.pinned) or move.start_piece[1] == 'K': # if is pinned piece or king piece
                    self.make_move(move, False)
                    check, _ = self.is_check()
                    if not check:
                        moves.append(move)
                    self.undo_move(False)
                else:
                    moves.append(move)
        return moves

    def get_possible_moves(self):
        moves = []
        for (r, rValue) in enumerate(self.board):
            for (c, piece) in enumerate(rValue):
                if piece == '--' or (piece[0] == 'b' and self.whiteToMove) \
                        or (piece[0] == 'w' and not self.whiteToMove):
                    continue
                piece_type = piece[1]
                if piece_type == 'P': # pawn
                    moves += self.get_pawn_moves(r, c)
                if piece_type == 'R': # Rock
                    moves += self.get_rock_moves(r, c)
                if piece_type == 'B': # bishop
                    moves += self.get_bishop_moves(r, c)
                if piece_type == 'N': # bishop
                    moves += self.get_knight_moves(r, c)
                if piece_type == 'Q': # queen
                    moves += self.get_queen_moves(r, c)
                if piece_type == 'K': # king
                    moves += self.get_king_moves(r, c)

        return moves

    def get_pawn_moves(self, r, c):
        moves = []
        if self.whiteToMove:
            if r == 6 and self.board[4][c] == '--' and self.board[5][c] == '--':
                moves.append(Move((r, c), (r-2, c), self.board))
            if r >= 1 and self.board[r-1][c] == '--':
                moves.append(Move((r, c), (r-1, c), self.board))
            if c >= 1 and self.board[r-1][c-1][0] == 'b':
                moves.append(Move((r, c), (r-1, c-1), self.board))
            if c <= 6 and self.board[r-1][c+1][0] == 'b':
                moves.append(Move((r, c), (r-1, c+1), self.board))
        else:
            if r == 1 and self.board[3][c] == '--' and self.board[2][c] == '--':
                moves.append(Move((r, c), (r+2, c), self.board))
            if r <= 6 and self.board[r+1][c] == '--':
                moves.append(Move((r, c), (r+1, c), self.board))
            if c >= 1 and self.board[r+1][c-1][0] == 'w':
                moves.append(Move((r, c), (r+1, c-1), self.board))
            if c <= 6 and self.board[r+1][c+1][0] == 'w':
                moves.append(Move((r, c), (r+1, c+1), self.board))
        return moves

    def get_rock_moves(self, r, c):
        return self.get_straight_moves(r, c)

    def get_bishop_moves(self, r, c):
        return self.get_diagonal_moves(r, c)

    def get_knight_moves(self, r, c):
        co_eff = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        return self.validate_and_create_moves(r, c, 1, co_eff)

    def get_queen_moves(self, r, c):
        moves = []
        moves += self.get_straight_moves(r, c)
        moves += self.get_diagonal_moves(r, c)
        return moves

    def get_king_moves(self, r, c):
        moves = []
        moves += self.get_straight_moves(r, c, 1)
        moves += self.get_diagonal_moves(r, c, 1)
        return moves

    def get_straight_moves(self, r, c, ra=100):
        co_eff = ((-1, 0), (1, 0), (0, -1), (0, 1))
        return self.validate_and_create_moves(r, c, ra, co_eff)

    def get_diagonal_moves(self, r, c, ra=100):
        co_eff = ((-1, 1), (1, 1), (1, -1), (-1, -1))
        return self.validate_and_create_moves(r, c, ra, co_eff)

    def validate_and_create_moves(self, r, c, ra, co_eff):
        moves = []
        for (x, y) in co_eff:
            tem_r = r + x
            tem_c = c + y
            tem_ra = 1
            while 0 <= tem_r < 8 and 0 <= tem_c < 8 and tem_ra <= ra:
                piece = self.board[tem_r][tem_c]
                if piece == '--':
                    moves.append(Move((r, c), (tem_r, tem_c), self.board))
                    tem_r += x
                    tem_c += y
                    tem_ra += 1
                    continue
                if self.is_enemy(piece[0]):
                    moves.append(Move((r, c), (tem_r, tem_c), self.board))
                break
        return moves

    def is_ally(self, piece_color):
        return (piece_color == 'w' and self.whiteToMove) or (piece_color == 'b' and not self.whiteToMove)

    def is_enemy(self, piece_color):
        return (piece_color == 'w' and not self.whiteToMove) or (piece_color == 'b' and self.whiteToMove)

    def is_pawn_or_knight_threat(self, w_co_eff, b_co_eff, piece_type):
        if self.whiteToMove:
            for (x, y) in w_co_eff:
                tem_r = self.wK_pos[0] + x
                tem_c = self.wK_pos[1] + y
                if 0 <= tem_r < 8 and 0 <= tem_c < 8 and self.board[tem_r][tem_c] == ('b' + piece_type):
                    return True
        else:
            for (x, y) in b_co_eff:
                tem_r = self.bK_pos[0] + x
                tem_c = self.bK_pos[1] + y
                if 0 <= tem_r < 8 and 0 <= tem_c < 8 and self.board[tem_r][tem_c] == ('w' + piece_type):
                    return True

    # check if in check state and return (isCheck, pinned pieces)
    def is_check(self):
        pinned = []
        # check pawn threat
        w_co_eff = ((-1, -1), (-1, 1))
        b_co_eff = ((1, -1), (1, 1))
        if self.is_pawn_or_knight_threat(w_co_eff, b_co_eff, 'P'):
            return True, None
        # check knight threat
        w_co_eff = b_co_eff = ((-2, 1), (-1, 2), (1, 2), (2, 1), (2, -1), (1, -2), (-1, -2), (-2, -1))
        if self.is_pawn_or_knight_threat(w_co_eff, b_co_eff, 'N'):
            return True, None
        # check the rest threat
        co_eff = ((-1, 0), (1, 0), (0, -1), (0, 1), (-1, 1), (1, 1), (1, -1), (-1, -1))
        (r, c) = self.wK_pos if self.whiteToMove else self.bK_pos
        for (i, (x, y)) in enumerate(co_eff):
            tem_r = r + x
            tem_c = c + y
            possible_pin = None
            count = 1
            while 0 <= tem_r < 8 and 0 <= tem_c < 8:
                piece = self.board[tem_r][tem_c]
                if self.is_ally(piece[0]): # if ally
                    if not possible_pin: # if the first time meet ally
                        possible_pin = (tem_r, tem_c)
                    else: # if the second time meet ally
                        break
                elif self.is_enemy(piece[0]): # if enemy
                    if (0 <= i < 4 and piece[1] == 'R') or (4 <= i < 8 and piece[1] == 'B') or piece[1] == 'Q' \
                            or (count == 1 and piece[1] == 'K'):
                        if not possible_pin: # if check
                            return True, None
                        else: # if there is a pinned ally
                            pinned.append(possible_pin)
                    break
                tem_r += x
                tem_c += y
                count += 1
        return False, pinned


class Move:
    rowToSym = {0: '8', 1: '7', 2: '6', 3: '5', 4: '4', 5: '3', 6: '2', 7: '1'}
    colToSym = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    def __init__(self, start_pos, end_pos, board):
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.start_piece = board[start_pos[0]][start_pos[1]]
        self.end_piece = board[end_pos[0]][end_pos[1]]
        self.is_promotion = False
        if (self.start_piece == 'wP' and end_pos[0] == 0) or (self.start_piece == 'bP' and end_pos[0] == 7):
            self.is_promotion = True

    def __eq__(self, other):
        if not isinstance(other, Move):
            return False
        return self.start_pos == other.start_pos and self.end_pos == other.end_pos \
               and self.start_piece == other.start_piece and self.end_piece == other.end_piece

    def get_notation(self):
        return self.colToSym[self.start_pos[1]] + self.rowToSym[self.start_pos[0]] + ' -> ' \
               + self.colToSym[self.end_pos[1]] + self.rowToSym[self.end_pos[0]]