"""搜索函数契约测试。

硬约束：
    1. 有棋可走时，search 必须返回一条**合法**走法
    2. 无棋可走时返回 None
    3. 不修改传入的棋盘
    4. 超时（time_limit 很小）也必须返回合法走法，不能返回 None / 崩溃

说明：测试里显式传较小的 depth / time_limit，避免 CI 因为搜索太慢而超时；
Minimax 的搜索强度由 docs/meeting/ 的性能记录单独验证，不放在单元测试里。
"""

from __future__ import annotations

import time

from board import ARROW, BLACK, WHITE, empty_board, idx, initial_board
from rule import is_legal
from ai_search import search, search_by_difficulty


def test_search_returns_legal_move_on_initial_board():
    board = initial_board()
    move = search(board, WHITE, depth=1, time_limit=2.0)
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
    # 走 depth=2 的分支，确保 do_move / undo_move 的回溯也被覆盖到
    search(board, WHITE, depth=2, time_limit=1.5, candidate_limit=8)
    assert board == snapshot, "search 不允许修改传入的棋盘"


def test_search_works_for_both_colors():
    board = initial_board()
    for color in (WHITE, BLACK):
        move = search(board, color, depth=1, time_limit=1.5)
        assert move is not None and is_legal(board, move, color)


def test_search_tiny_time_limit_still_returns_legal_move():
    """time_limit=0.01 秒：必须立刻退回一条合法走法，不能卡住或崩溃。"""
    board = initial_board()
    started = time.perf_counter()
    move = search(board, WHITE, depth=2, time_limit=0.01)
    elapsed = time.perf_counter() - started

    assert move is not None, "有时间上限时也必须返回走法"
    assert is_legal(board, move, WHITE), "超时退化的走法必须合法"
    assert elapsed < 2.0, f"time_limit=0.01 却用了 {elapsed:.2f} 秒，时限控制没生效"


def test_search_depth_two_with_candidate_limit():
    """depth=2 + 候选裁剪：验证 Minimax 递归路径可用且结果合法。"""
    board = initial_board()
    move = search(board, WHITE, depth=2, time_limit=1.5, candidate_limit=8)
    assert move is not None and is_legal(board, move, WHITE)


def test_search_by_difficulty_easy_is_legal():
    board = initial_board()
    move = search_by_difficulty(board, WHITE, "easy")
    assert move is not None and is_legal(board, move, WHITE)


def test_search_by_difficulty_unknown_falls_back_to_normal():
    board = initial_board()
    # 未知难度按 normal 处理；只断言返回合法走法，不依赖具体强度
    move = search_by_difficulty(board, WHITE, "unknown")
    assert move is not None and is_legal(board, move, WHITE)
