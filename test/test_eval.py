"""估值函数契约测试。

这些断言是**硬约束**，实现可以改，但必须一直通过：
    1. 零和一致性：evaluate(board, WHITE) == -evaluate(board, BLACK)
    2. 纯函数：evaluate 不修改传入的棋盘
    3. Evaluator 自定义权重后仍然满足零和

TODO(@qiqiyuexi)：往这个文件里补充你自己特征的用例，例如
    - 位置权值表：中心格子的分应高于角落
    - 我方棋子越多、可走格数越多，分数应越高
    - 同一局面下 WHITE 与 BLACK 的分数严格相反
"""

from __future__ import annotations

from ai_eval import DEFAULT_WEIGHTS, Evaluator, evaluate
from board import ARROW, BLACK, WHITE, empty_board, idx, initial_board


def test_zero_sum_on_initial_and_empty_board():
    for board in (initial_board(), empty_board()):
        assert evaluate(board, WHITE) == -evaluate(board, BLACK)


def test_zero_sum_on_handmade_position():
    board = empty_board()
    board[idx(4, 4)] = WHITE
    board[idx(5, 5)] = BLACK
    board[idx(0, 0)] = ARROW
    assert evaluate(board, WHITE) == -evaluate(board, BLACK)


def test_evaluate_does_not_mutate_board():
    board = initial_board()
    snapshot = board[:]
    evaluate(board, WHITE)
    evaluate(board, BLACK)
    assert board == snapshot, "evaluate 不允许修改传入的棋盘"


def test_empty_board_scores_zero():
    board = empty_board()
    assert evaluate(board, WHITE) == 0
    assert evaluate(board, BLACK) == 0


def test_evaluator_with_custom_weights_is_still_zero_sum():
    board = initial_board()
    for weights in ({"mobility": 2.0}, {"territory": 0.0}, {"position": 1.0}):
        evaluator = Evaluator(weights)
        assert evaluator.evaluate(board, WHITE) == -evaluator.evaluate(board, BLACK)


def test_weights_have_expected_keys():
    """权重的键名发生变化时提醒一下（AI/报告里都按这些名字引用）。"""
    for key in ("mobility", "territory", "position"):
        assert key in DEFAULT_WEIGHTS
