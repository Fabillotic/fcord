import fcord
from fcord import relative as rel
import util
import chess_mod
from requests import request
import convert
import os
from PIL import Image
import chess
from chess import Board, Move

def register():
    util.register_game("chess", chess_mod.get_moves(), chess_mod.move, chess_mod.get_default(), chess_mod.send_help)

def init():
    if not os.path.exists(rel("mods/chess/images/chess-rook_white.png")): #Just a basic check
        convert.start()

    chess_mod.images["board"] = Image.open(rel("mods/chess/images/board.png"))
    chess_mod.images["b"] = Image.open(rel("mods/chess/images/chess-bishop_black.png"))
    chess_mod.images["B"] = Image.open(rel("mods/chess/images/chess-bishop_white.png"))
    chess_mod.images["k"] = Image.open(rel("mods/chess/images/chess-king_black.png"))
    chess_mod.images["K"] = Image.open(rel("mods/chess/images/chess-king_white.png"))
    chess_mod.images["n"] = Image.open(rel("mods/chess/images/chess-knight_black.png"))
    chess_mod.images["N"] = Image.open(rel("mods/chess/images/chess-knight_white.png"))
    chess_mod.images["p"] = Image.open(rel("mods/chess/images/chess-pawn_black.png"))
    chess_mod.images["P"] = Image.open(rel("mods/chess/images/chess-pawn_white.png"))
    chess_mod.images["q"] = Image.open(rel("mods/chess/images/chess-queen_black.png"))
    chess_mod.images["Q"] = Image.open(rel("mods/chess/images/chess-queen_white.png"))
    chess_mod.images["r"] = Image.open(rel("mods/chess/images/chess-rook_black.png"))
    chess_mod.images["R"] = Image.open(rel("mods/chess/images/chess-rook_white.png"))

def get_default():
    return chess.STARTING_FEN

def get_moves():
    x = []
    for y in range(1, 9):
        a = chr(96 + y)
        for z in range(1, 9):
            x.append(a + str(z))
    return [x, x, [None, "queen", "rook", "bishop", "knight", "q", "r", "b", "n"]]

def move(e, move_in, player, state, preview):
    board = Board(state)
    
    if preview:
        send_board(board, e["d"]["channel_id"])
        return
    
    invalid = False
    move = None
    try:
        move = Move(chess.parse_square(move_in[0]), chess.parse_square(move_in[1]), None)
    except:
        invalid = True
        print("Exception on move generation!")
    if chess.square_rank(move.to_square) + 1 == 8:
        print("promotion!")
        move.promotion = get_piece_type(move_in[2])
    print("move:", move)
    print("input:", move_in)
    print("state:", state)
    print("legal moves:", list(board.legal_moves))
    invalid = invalid or not move in board.legal_moves
    if invalid:
        fcord.send("Invalid move!", e["d"]["channel_id"])
        return

    board.push(move)
    send_board(board, e["d"]["channel_id"])
    
    if board.is_game_over():
        if board.is_checkmate():
            fcord.send("CHECKMATE!", e["d"]["channel_id"])
        elif board.is_stalemate():
            fcord.send("Stalemate.", e["d"]["channel_id"])
        elif board.is_insufficient_material():
            fcord.send("Insufficient material!", e["d"]["channel_id"])
        fcord.send("Game over! Result: " + board.result(), e["d"]["channel_id"])
        return board.fen(), True

    return board.fen(), False

def get_piece_type(name):
    if name == "queen" or name == "q":
        return chess.QUEEN
    elif name == "rook" or name == "r":
        return chess.ROOK
    elif name == "bishop" or name == "b":
        return chess.BISHOP
    elif name == "knight" or name == "n":
        return chess.KNIGHT
    else:
        return chess.QUEEN

chess_mod.images = {}

def send_board(board, channel):
    img = chess_mod.images["board"].copy()

    for i in range(64):
        x = (i // 8) * 512 + 256
        y = (i % 8) * 512 + 256

        p = board.piece_map().get(i)
        if not p:
            continue
        p = chess_mod.images[p.symbol()]
        img.paste(p, (x, y), p)
    
    o = rel("mods/chess/images/out.png")
    img.save(o)
    img.close()

    f = open(o, "rb")
    d = f.read()
    f.close()

    r = request("POST", "https://discord.com/api/channels/" + channel + "/messages", headers={"Authorization": "Bot " + fcord.token, "User-Agent": fcord.user_agent}, files={"img.png": d, "payload_json": (None, '{"content": "Board:", "embed": {"image": {"url": "attachment://img.png"}}}'.encode("utf-8"))})

    os.remove(o)

def send_help(c):
    fcord.send("Can't help ya right now.", c)
