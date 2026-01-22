from flask import Flask, render_template, request, jsonify
import random

app = Flask(__name__)

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

def check_winner(board):
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(cell != "" for cell in board):
        return "DRAW"
    return None

def available_moves(board):
    return [i for i, v in enumerate(board) if v == ""]

def find_winning_move(board, player):
    for m in available_moves(board):
        board[m] = player
        if check_winner(board) == player:
            board[m] = ""
            return m
        board[m] = ""
    return None

def minimax(board, is_maximizing):
    res = check_winner(board)
    if res == "O":
        return 1
    if res == "X":
        return -1
    if res == "DRAW":
        return 0

    if is_maximizing:
        best = -10
        for m in available_moves(board):
            board[m] = "O"
            best = max(best, minimax(board, False))
            board[m] = ""
        return best
    else:
        best = 10
        for m in available_moves(board):
            board[m] = "X"
            best = min(best, minimax(board, True))
            board[m] = ""
        return best

def best_move_hard(board):
    if board.count("") == 9:
        return 4
    best_score = -10
    best_move = None
    for m in available_moves(board):
        board[m] = "O"
        score = minimax(board, False)
        board[m] = ""
        if score > best_score:
            best_score = score
            best_move = m
    return best_move

def best_move_medium(board):
    m = find_winning_move(board, "O")
    if m is not None:
        return m
    m = find_winning_move(board, "X")
    if m is not None:
        return m
    if board[4] == "":
        return 4
    corners = [c for c in [0, 2, 6, 8] if board[c] == ""]
    if corners:
        return random.choice(corners)
    edges = [e for e in [1, 3, 5, 7] if board[e] == ""]
    if edges:
        return random.choice(edges)
    return None

def best_move_easy(board):
    return random.choice(available_moves(board))

def pick_bot_move(board, difficulty):
    if difficulty == "hard":
        return best_move_hard(board)
    if difficulty == "medium":
        return best_move_medium(board)
    return best_move_easy(board)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json()
    board = data["board"]
    idx = data["index"]
    difficulty = data["difficulty"]

    board[idx] = "X"
    res = check_winner(board)
    if res:
        return jsonify(board=board, winner=res)

    bm = pick_bot_move(board, difficulty)
    board[bm] = "O"
    res = check_winner(board)

    return jsonify(board=board, winner=res)
