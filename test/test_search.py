"""搜索函数契约测试。

硬约束：
    1. 有棋可走时，search 必须返回一条**合法**走法
    2. 无棋可走时返回 None
    3. 不修改传入的棋盘

TODO(@wyhsy)：M3 换成 Minimax 之后，可以再加这些用例：
    - depth 越大不一定更强，但必须仍然返回合法走法
    - time_limit 很小时（如 0.01 秒）也必须返回合法走法，不能返回 None/崩溃
"""

from __future__ import annotations

from board import ARROW, BLACK, WHITE, empty_board, idx, initial_board
from rule import is_legal
from ai_search import search


def test_search_returns_legal_move_on_initial_board():
    board = initial_board()
    move = search(board, WHITE)
    assert move is not None, "开局有棋可走，不应返回 None"
    assert is_legal(board, move, WHITE), "search 返回了非法走法"


def test_search_returns_none_when_no_move():
    board = empty_board()
    board[idx(4, 4)] = WHITE
    for r in range(3, 6):
        for c in range(3, 6):
            if (r, c) != (4, 4):
                board[idx(r, c)] = ARROW

    assert search(board, WHITE) is None


def test_search_does_not_mutate_board():
    board = initial_board()
    snapshot = board[:]
    search(board, WHITE)
    assert board == snapshot, "search 不允许修改传入的棋盘"


def test_search_works_for_both_colors():
    board = initial_board()
    for color in (WHITE, BLACK):
        move = search(board, color)
        assert move is not None and is_legal(board, move, color)
