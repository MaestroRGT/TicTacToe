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

# ---------- HARD (minimax) ----------
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
    # take center first sometimes
    if board.count("") == 9:
        return random.choice([0, 2, 4, 6, 8])  # vary openings

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

# ---------- MEDIUM (win/block + heuristics) ----------
def best_move_medium(board):
    # 1) win now
    m = find_winning_move(board, "O")
    if m is not None:
        return m
    # 2) block human win
    m = find_winning_move(board, "X")
    if m is not None:
        return m
    # 3) center
    if board[4] == "":
        return 4
    # 4) corners
    corners = [c for c in [0, 2, 6, 8] if board[c] == ""]
    if corners:
        return random.choice(corners)
    # 5) edges
    edges = [e for e in [1, 3, 5, 7] if board[e] == ""]
    if edges:
        return random.choice(edges)
    return random.choice(available_moves(board))

# ---------- EASY (random) ----------
def best_move_easy(board):
    moves = available_moves(board)
    return random.choice(moves) if moves else None

def pick_bot_move(board, difficulty):
    difficulty = (difficulty or "easy").lower()

    # ✅ Important: on introduit une "faute" ~25% du temps
    # pour éviter "toujours nul" sur hard.
    # La faute est aléatoire et peut arriver à n'importe quel tour.
    mistake_rate = 0.25

    if difficulty == "hard":
        if random.random() < mistake_rate:
            # play a "not optimal" move: prefer random non-winning move
            moves = available_moves(board)
            random.shuffle(moves)
            # avoid immediate winning move if we want to be beatable
            win = find_winning_move(board, "O")
            if win in moves:
                moves.remove(win)
            return moves[0] if moves else None
        return best_move_hard(board)

    if difficulty == "medium":
        # medium can also make small mistakes but less
        if random.random() < 0.10:
            return best_move_easy(board)
        return best_move_medium(board)

    # easy
    return best_move_easy(board)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/move", methods=["POST"])
def move():
    data = request.get_json(force=True)

    board = data.get("board")
    idx = data.get("index")
    difficulty = data.get("difficulty", "easy")
    mode = data.get("mode", "ai")       # "ai" or "local"
    turn = data.get("turn", "X")        # for local mode: whose turn is playing

    if not isinstance(board, list) or len(board) != 9:
        return jsonify(error="Board invalide"), 400
    if idx is None or not isinstance(idx, int) or not (0 <= idx <= 8):
        return jsonify(error="Index invalide"), 400

    board = [("" if v is None else str(v)) for v in board]

    # If game already ended
    res = check_winner(board)
    if res is not None:
        return jsonify(board=board, winner=res), 200

    if board[idx] != "":
        return jsonify(error="Case déjà prise"), 400

    # -------- LOCAL 2 PLAYERS (no AI) --------
    if mode == "local":
        # Just place the symbol sent by the client (X or O)
        if turn not in ["X", "O"]:
            return jsonify(error="Turn invalide"), 400
        board[idx] = turn
        res = check_winner(board)
        return jsonify(board=board, winner=res), 200

    # -------- AI MODE (Human X, Bot O) --------
    board[idx] = "X"
    res = check_winner(board)
    if res is not None:
        return jsonify(board=board, winner=res), 200

    bm = pick_bot_move(board, difficulty)
    if bm is not None and board[bm] == "":
        board[bm] = "O"

    res = check_winner(board)
    return jsonify(board=board, winner=res), 200

if __name__ == "__main__":
    app.run(debug=True)
