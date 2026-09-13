"""规则引擎契约测试（M1 验收核心）。

约定：开局布局与走法规则一旦确定，就以本文件的断言为准。
若课程题目册和这里有出入，**先改测试、再改实现**（见 docs/interface.md 第 2 节）。

跑法：pytest -q
"""

from __future__ import annotations

import random

from board import ARROW, BLACK, EMPTY, WHITE, at, empty_board, idx, initial_board
from rule import (
    BLACK_WIN,
    DRAW,
    Move,
    apply_move,
    do_move,
    game_result,
    has_any_move,
    is_legal,
    legal_moves,
    piece_targets,
    territory,
    undo_move,
)


# --------------------------------------------------------------- 开局布局

def test_initial_board_layout():
    """标准开局：黑 (0,3)、(3,0)、(6,9)、(9,6)；白 (0,6)、(3,9)、(6,0)、(9,3)。"""
    board = initial_board()
    assert len(board) == 100
    assert board.count(BLACK) == 4
    assert board.count(WHITE) == 4
    assert board.count(ARROW) == 0

    for r, c in ((0, 3), (3, 0), (6, 9), (9, 6)):
        assert at(board, r, c) == BLACK, f"黑棋 {r},{c} 位置不对"
    for r, c in ((0, 6), (3, 9), (6, 0), (9, 3)):
        assert at(board, r, c) == WHITE, f"白棋 {r},{c} 位置不对"
    for r, c in ((0, 0), (4, 4), (5, 5), (9, 9)):
        assert at(board, r, c) == EMPTY


# --------------------------------------------------------------- 走法生成

def test_piece_targets_center_on_empty_board():
    """空棋盘正中央 (4,4)：8 个方向合计 4+5+4+5+4+4+4+5 = 35 格。"""
    board = empty_board()
    board[idx(4, 4)] = WHITE
    assert len(piece_targets(board, 4, 4)) == 35


def test_piece_targets_corner_on_empty_board():
    """空棋盘角落 (0,0)：右 9 + 下 9 + 右下 9 = 27 格。"""
    board = empty_board()
    board[idx(0, 0)] = WHITE
    assert len(piece_targets(board, 0, 0)) == 27


def test_no_knight_moves():
    """题目册只规定"行棋方法与皇后相同"，没有马步。"""
    board = empty_board()
    board[idx(0, 0)] = WHITE
    targets = piece_targets(board, 0, 0)
    assert (1, 2) not in targets, "出现了马步 (1,2)，走法实现错了"
    assert (2, 1) not in targets, "出现了马步 (2,1)，走法实现错了"


def test_cannot_jump_over_obstacles():
    """路径上有东西就必须停下，不能穿过去。"""
    board = empty_board()
    board[idx(0, 0)] = WHITE
    board[idx(0, 3)] = ARROW
    targets = piece_targets(board, 0, 0)
    assert (0, 1) in targets and (0, 2) in targets
    assert (0, 3) not in targets
    assert (0, 4) not in targets and (0, 9) not in targets


def test_legal_moves_in_initial_position():
    """开局每方走法数千条，黑白数量相同（布局左右对称）。"""
    board = initial_board()
    white_moves = legal_moves(board, WHITE)
    black_moves = legal_moves(board, BLACK)

    assert len(white_moves) == len(black_moves)
    assert 1800 <= len(white_moves) <= 2400, (
        f"开局走法数 {len(white_moves)} 不在预期区间"
        "（标准亚马逊棋约 2176 条），请检查开局布局与走法规则"
    )
    assert len(set(white_moves)) == len(white_moves), "生成的走法有重复"

    for move in white_moves:
        assert len(move.src) == 2 and len(move.dst) == 2 and len(move.arrow) == 2
        assert move.arrow != move.dst, "箭不能射在自己落点的格子上"
        assert board[idx(*move.src)] == WHITE


# --------------------------------------------------------------- 合法性校验

def test_is_legal():
    board = initial_board()
    move = legal_moves(board, WHITE)[0]

    assert is_legal(board, move, WHITE)
    assert not is_legal(board, move, BLACK), "黑方不能替白方走棋"

    bad_arrow = Move(move.src, move.dst, move.dst)
    assert not is_legal(board, bad_arrow, WHITE), "箭不能射到自己落点（该格已被占住）"

    bad_src = Move((9, 9), (9, 8), (9, 7))
    assert not is_legal(board, bad_src, WHITE), "起点上没有己方棋子，应判非法"


def test_apply_move_keeps_input_untouched():
    board = initial_board()
    snapshot = board[:]
    move = legal_moves(board, WHITE)[0]
    after = apply_move(board, move, WHITE)

    assert board == snapshot, "apply_move 不允许修改传入的棋盘"
    assert after[idx(*move.src)] == EMPTY
    assert after[idx(*move.dst)] == WHITE
    assert after[idx(*move.arrow)] == ARROW
    assert after.count(WHITE) == 4 and after.count(BLACK) == 4
    assert after.count(ARROW) == 1


def test_do_move_and_undo_move_roundtrip():
    board = initial_board()
    snapshot = board[:]
    move = legal_moves(board, WHITE)[0]

    old = do_move(board, move, WHITE)
    assert board != snapshot
    assert board.count(ARROW) == 1

    undo_move(board, move, WHITE, old)
    assert board == snapshot, "undo_move 必须把棋盘完全恢复"


# --------------------------------------------------------------- 终局判定

def _seal_white_at_4_4(board):
    """把 (4,4) 上白棋的 8 个邻格全用箭头封死。"""
    for r in range(3, 6):
        for c in range(3, 6):
            if (r, c) != (4, 4):
                board[idx(r, c)] = ARROW


def test_has_any_move_and_win():
    board = empty_board()
    board[idx(4, 4)] = WHITE
    board[idx(0, 0)] = BLACK
    assert has_any_move(board, WHITE)
    assert has_any_move(board, BLACK)
    assert game_result(board) is None

    _seal_white_at_4_4(board)
    assert not has_any_move(board, WHITE)
    assert has_any_move(board, BLACK)
    assert game_result(board) == BLACK_WIN


def test_draw_when_both_sides_stuck():
    board = empty_board()
    board[idx(4, 4)] = WHITE
    board[idx(0, 0)] = BLACK

    _seal_white_at_4_4(board)
    for r in range(0, 2):
        for c in range(0, 2):
            if (r, c) != (0, 0):
                board[idx(r, c)] = ARROW

    assert not has_any_move(board, WHITE)
    assert not has_any_move(board, BLACK)
    assert game_result(board) == DRAW


# --------------------------------------------------------------- 领地数据

def test_territory_counts_free_neighbours_only():
    board = empty_board()
    board[idx(4, 4)] = WHITE

    black_t, white_t = territory(board)
    assert black_t == 0
    assert white_t == 8, "正中央的孤子周围 8 格都是空的"

    board[idx(3, 3)] = ARROW
    black_t, white_t = territory(board)
    assert white_t == 7, "被箭头占住的格子不算领地"


# --------------------------------------------------------------- 集成：随机对局

def test_random_game_50_steps():
    """随机对局 50 步：每步都合法，且没有棋子被吃、箭头数量等于步数。"""
    rng = random.Random(20260913)
    board = initial_board()
    color = WHITE
    steps = 0

    while steps < 50 and game_result(board) is None:
        moves = legal_moves(board, color)
        assert moves, f"{color} 还有棋可走时却生成了空走法列表"
        move = rng.choice(moves)
        assert is_legal(board, move, color), "从 legal_moves 里挑出的走法竟然非法"
        board = apply_move(board, move, color)
        steps += 1
        color = BLACK if color == WHITE else WHITE

    assert board.count(WHITE) == 4, "白方棋子被吃掉了（规则不允许）"
    assert board.count(BLACK) == 4, "黑方棋子被吃掉了（规则不允许）"
    assert board.count(ARROW) == steps, "箭头数量必须等于已走步数"
    assert steps > 0
