import copy
import math
import tkinter as tk
from tkinter import messagebox

BOARD_SIZE = 8
SQUARE_SIZE = 80
WINDOW_PADDING = 24

HUMAN = "r"  # Red pieces (human), move upward.
AI = "b"     # Black pieces (computer), move downward.

DIRECTIONS = {
    "r": [(-1, -1), (-1, 1)],
    "b": [(1, -1), (1, 1)],
    "R": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    "B": [(-1, -1), (-1, 1), (1, -1), (1, 1)],
}


class CheckersGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Checkers (Human vs Computer)")

        canvas_size = BOARD_SIZE * SQUARE_SIZE
        self.canvas = tk.Canvas(
            root,
            width=canvas_size,
            height=canvas_size,
            bg="#f6f1e7",
            highlightthickness=0,
        )
        self.canvas.pack(padx=WINDOW_PADDING, pady=(WINDOW_PADDING, 8))

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, font=("Helvetica", 13))
        self.status_label.pack(pady=(0, 8))

        self.reset_btn = tk.Button(root, text="New Game", command=self.reset_game, font=("Helvetica", 12))
        self.reset_btn.pack(pady=(0, WINDOW_PADDING))

        self.board = self.create_initial_board()
        self.turn = HUMAN
        self.selected = None
        self.legal_moves = []
        self.multi_jump_piece = None
        self.game_over = False

        self.canvas.bind("<Button-1>", self.on_click)

        self.update_status()
        self.draw()

    def create_initial_board(self):
        board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

        for row in range(3):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    board[row][col] = "b"

        for row in range(5, 8):
            for col in range(BOARD_SIZE):
                if (row + col) % 2 == 1:
                    board[row][col] = "r"

        return board

    def reset_game(self):
        self.board = self.create_initial_board()
        self.turn = HUMAN
        self.selected = None
        self.legal_moves = []
        self.multi_jump_piece = None
        self.game_over = False
        self.update_status()
        self.draw()

    def update_status(self):
        if self.game_over:
            return

        if self.turn == HUMAN:
            text = "Your turn (Red). Click a piece to move."
        else:
            text = "Computer is thinking..."

        if self.multi_jump_piece is not None and self.turn == HUMAN:
            text = "Must continue jump with selected piece."

        self.status_var.set(text)

    def draw(self):
        self.canvas.delete("all")

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x0 = col * SQUARE_SIZE
                y0 = row * SQUARE_SIZE
                x1 = x0 + SQUARE_SIZE
                y1 = y0 + SQUARE_SIZE

                color = "#8B5A2B" if (row + col) % 2 else "#F0D9B5"
                self.canvas.create_rectangle(x0, y0, x1, y1, fill=color, outline="")

        # highlight selected piece
        if self.selected is not None:
            r, c = self.selected
            self.highlight_square(r, c, "#ffd166", width=4)

        # highlight legal targets
        for move in self.legal_moves:
            _, _, tr, tc, _ = move
            self.highlight_square(tr, tc, "#4cc9f0", width=3)

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                piece = self.board[row][col]
                if piece:
                    self.draw_piece(row, col, piece)

    def draw_piece(self, row, col, piece):
        x0 = col * SQUARE_SIZE + 10
        y0 = row * SQUARE_SIZE + 10
        x1 = x0 + SQUARE_SIZE - 20
        y1 = y0 + SQUARE_SIZE - 20

        is_red = piece.lower() == "r"
        color = "#d62828" if is_red else "#1d3557"
        self.canvas.create_oval(x0, y0, x1, y1, fill=color, outline="#111", width=2)

        if piece.isupper():
            cx = (x0 + x1) / 2
            cy = (y0 + y1) / 2
            self.canvas.create_text(
                cx,
                cy,
                text="K",
                fill="#ffeb3b",
                font=("Helvetica", 20, "bold"),
            )

    def highlight_square(self, row, col, color, width=3):
        x0 = col * SQUARE_SIZE + 2
        y0 = row * SQUARE_SIZE + 2
        x1 = x0 + SQUARE_SIZE - 4
        y1 = y0 + SQUARE_SIZE - 4
        self.canvas.create_rectangle(x0, y0, x1, y1, outline=color, width=width)

    def on_click(self, event):
        if self.game_over or self.turn != HUMAN:
            return

        col = event.x // SQUARE_SIZE
        row = event.y // SQUARE_SIZE
        if not self.in_bounds(row, col):
            return

        if self.multi_jump_piece is not None:
            if self.selected != self.multi_jump_piece:
                self.selected = self.multi_jump_piece
                self.legal_moves = self.get_moves_for_piece(self.board, self.turn, *self.selected, must_capture=True)

            matched = [m for m in self.legal_moves if m[2] == row and m[3] == col]
            if matched:
                self.apply_human_move(matched[0])
            self.draw()
            return

        piece = self.board[row][col]
        if piece and self.is_current_players_piece(piece, HUMAN):
            must_capture = self.player_has_capture(self.board, HUMAN)
            self.selected = (row, col)
            self.legal_moves = self.get_moves_for_piece(self.board, HUMAN, row, col, must_capture)
            self.draw()
            return

        if self.selected is not None:
            matched = [m for m in self.legal_moves if m[2] == row and m[3] == col]
            if matched:
                self.apply_human_move(matched[0])
                self.draw()

    def apply_human_move(self, move):
        self.board = self.apply_move(self.board, move)
        sr, sc, tr, tc, captured = move

        if captured:
            piece = self.board[tr][tc]
            next_captures = self.get_moves_for_piece(self.board, HUMAN, tr, tc, must_capture=True)
            if next_captures and piece and self.is_current_players_piece(piece, HUMAN):
                self.multi_jump_piece = (tr, tc)
                self.selected = (tr, tc)
                self.legal_moves = next_captures
                self.update_status()
                return

        self.multi_jump_piece = None
        self.selected = None
        self.legal_moves = []

        winner = self.get_winner(self.board)
        if winner:
            self.end_game(winner)
            return

        self.turn = AI
        self.update_status()
        self.draw()
        self.root.after(180, self.computer_turn)

    def computer_turn(self):
        if self.game_over or self.turn != AI:
            return

        move = self.choose_ai_move(self.board)
        if move is None:
            self.end_game(HUMAN)
            return

        self.board = self.apply_move(self.board, move)
        sr, sc, tr, tc, captured = move

        # continue forced jumps for AI automatically with greedy fallback.
        while captured:
            options = self.get_moves_for_piece(self.board, AI, tr, tc, must_capture=True)
            if not options:
                break
            next_move = self.best_local_capture(self.board, options)
            self.board = self.apply_move(self.board, next_move)
            _, _, tr, tc, captured = next_move

        winner = self.get_winner(self.board)
        if winner:
            self.end_game(winner)
            return

        self.turn = HUMAN
        self.update_status()
        self.draw()

    def end_game(self, winner):
        self.game_over = True
        if winner == HUMAN:
            msg = "You win!"
        elif winner == AI:
            msg = "Computer wins!"
        else:
            msg = "Draw!"

        self.status_var.set(msg)
        self.draw()
        messagebox.showinfo("Game Over", msg)

    def get_winner(self, board):
        red_count = 0
        black_count = 0

        for row in board:
            for piece in row:
                if piece is None:
                    continue
                if piece.lower() == "r":
                    red_count += 1
                else:
                    black_count += 1

        if red_count == 0:
            return AI
        if black_count == 0:
            return HUMAN

        red_moves = self.get_all_moves(board, HUMAN)
        black_moves = self.get_all_moves(board, AI)
        if not red_moves:
            return AI
        if not black_moves:
            return HUMAN

        return None

    def choose_ai_move(self, board):
        moves = self.get_all_moves(board, AI)
        if not moves:
            return None

        depth = 5
        best_score = -math.inf
        best_move = moves[0]

        for move in moves:
            new_board = self.apply_move(board, move)
            score = self.minimax(new_board, depth - 1, -math.inf, math.inf, maximizing=False)
            if score > best_score:
                best_score = score
                best_move = move

        return best_move

    def minimax(self, board, depth, alpha, beta, maximizing):
        winner = self.get_winner(board)
        if winner == AI:
            return 100000
        if winner == HUMAN:
            return -100000

        if depth == 0:
            return self.evaluate(board)

        player = AI if maximizing else HUMAN
        moves = self.get_all_moves(board, player)
        if not moves:
            return self.evaluate(board)

        if maximizing:
            value = -math.inf
            for move in moves:
                new_board = self.apply_move(board, move)
                value = max(value, self.minimax(new_board, depth - 1, alpha, beta, False))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value

        value = math.inf
        for move in moves:
            new_board = self.apply_move(board, move)
            value = min(value, self.minimax(new_board, depth - 1, alpha, beta, True))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

    def evaluate(self, board):
        score = 0

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece is None:
                    continue

                if piece == "b":
                    score += 10
                    score += r * 0.3
                    if 1 <= c <= 6:
                        score += 0.2
                elif piece == "B":
                    score += 17
                elif piece == "r":
                    score -= 10
                    score -= (7 - r) * 0.3
                    if 1 <= c <= 6:
                        score -= 0.2
                elif piece == "R":
                    score -= 17

        # mobility bonus
        score += 0.1 * len(self.get_all_moves(board, AI))
        score -= 0.1 * len(self.get_all_moves(board, HUMAN))

        return score

    def best_local_capture(self, board, capture_moves):
        best = capture_moves[0]
        best_val = -math.inf
        for move in capture_moves:
            val = self.evaluate(self.apply_move(board, move))
            if val > best_val:
                best_val = val
                best = move
        return best

    def get_all_moves(self, board, player):
        must_capture = self.player_has_capture(board, player)
        moves = []

        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece and self.is_current_players_piece(piece, player):
                    moves.extend(self.get_moves_for_piece(board, player, r, c, must_capture))

        return moves

    def player_has_capture(self, board, player):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                piece = board[r][c]
                if piece and self.is_current_players_piece(piece, player):
                    captures = self.get_moves_for_piece(board, player, r, c, must_capture=True)
                    if captures:
                        return True
        return False

    def get_moves_for_piece(self, board, player, row, col, must_capture=False):
        piece = board[row][col]
        if piece is None or not self.is_current_players_piece(piece, player):
            return []

        dirs = DIRECTIONS[piece]
        captures = []
        normals = []

        for dr, dc in dirs:
            nr, nc = row + dr, col + dc
            jr, jc = row + 2 * dr, col + 2 * dc

            if self.in_bounds(nr, nc):
                target = board[nr][nc]
                if target is None and not must_capture:
                    normals.append((row, col, nr, nc, []))

            if self.in_bounds(jr, jc) and self.in_bounds(nr, nc):
                mid_piece = board[nr][nc]
                landing = board[jr][jc]
                if mid_piece and self.is_opponent_piece(mid_piece, player) and landing is None:
                    captures.append((row, col, jr, jc, [(nr, nc)]))

        if must_capture:
            return captures
        return captures if captures else normals

    def apply_move(self, board, move):
        sr, sc, tr, tc, captured = move
        new_board = copy.deepcopy(board)

        piece = new_board[sr][sc]
        new_board[sr][sc] = None
        new_board[tr][tc] = piece

        for cr, cc in captured:
            new_board[cr][cc] = None

        # promotion
        if piece == "r" and tr == 0:
            new_board[tr][tc] = "R"
        elif piece == "b" and tr == BOARD_SIZE - 1:
            new_board[tr][tc] = "B"

        return new_board

    def is_current_players_piece(self, piece, player):
        return piece.lower() == player

    def is_opponent_piece(self, piece, player):
        return piece.lower() != player

    @staticmethod
    def in_bounds(r, c):
        return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def main():
    root = tk.Tk()
    game = CheckersGame(root)
    game.draw()
    root.mainloop()


if __name__ == "__main__":
    main()
