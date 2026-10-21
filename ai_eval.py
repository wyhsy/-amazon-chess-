"""局面估值（M2 阶段骨架）。

契约（docs/interface.md 第 4 节）：
    evaluate(board, color) -> int   # 正数表示对 color 有利，负数不利
    Evaluator(weights=None).evaluate(board, color) -> int

硬约束（测试里会检查）：
    1. **零和一致性**：evaluate(board, WHITE) == -evaluate(board, BLACK)
       —— 本文件用"永远以白方视角算一次，再按 color 取正负"来保证，天然成立。
    2. **纯函数**：不允许修改传入的 board。
    3. 不允许 import pygame / ui。

已完成：机动性（可走格数差）+ 领地（8 邻域空格差）+ 可调权重框架。
TODO（@qiqiyuexi —— 见 docs/tasks/M1-任务派发.md 任务卡 3）：
    1. 把 _position_score 换成真正的**位置权值表**（例如靠近中心/角落的差异化分值）
    2. 增加更多特征：连通性、空间分割、箭头对己方活动力的影响等
    3. 通过实际对局调 DEFAULT_WEIGHTS（把实验数据记进报告）
"""

from __future__ import annotations

from board import BLACK, BOARD_SIZE, WHITE
from rule import piece_targets, territory

# 各项特征的权重（可以调；改动后记得跑 test/test_eval.py）
DEFAULT_WEIGHTS = {
    "mobility": 1.0,    # 机动性：双方可走格数之差
    "territory": 0.5,   # 领地：8 方向紧邻空格数之差
    "position": 0.2,    # 位置：目前恒为 0，等权值表补上后生效
}


def _mobility(board, color: int) -> int:
    """该方所有棋子的可走格数之和。"""
    total = 0
    for i, value in enumerate(board):
        if value == color:
            total += len(piece_targets(board, i // BOARD_SIZE, i % BOARD_SIZE))
    return total


def _position_score(board, color: int) -> int:
    """位置分。

    TODO(@qiqiyuexi)：实现位置权值表。提示：
        - 10×10 棋盘中心区域（如 3~6 行列）给正分，四个角落给负分；
        - 可以预先算好一张 100 长度的表 POSITION_TABLE，循环累加即可。
    现在先返回 0，保证整体逻辑能跑通、测试能过。
    """
    return 0


def _white_perspective(board, weights: dict) -> float:
    """永远以白方视角计算一次得分（这样零和一致性自动成立）。"""
    black_territory, white_territory = territory(board)

    score = 0.0
    score += weights["mobility"] * (_mobility(board, WHITE) - _mobility(board, BLACK))
    score += weights["territory"] * (white_territory - black_territory)
    score += weights["position"] * (
        _position_score(board, WHITE) - _position_score(board, BLACK)
    )
    return score


def evaluate(board, color: int) -> int:
    """返回局面分数：正数对 color 有利。"""
    score = int(round(_white_perspective(board, DEFAULT_WEIGHTS)))
    return score if color == WHITE else -score


class Evaluator:
    """可配置权重的估值器（AI 调参时用）。"""

    def __init__(self, weights: dict | None = None) -> None:
        self.weights = dict(DEFAULT_WEIGHTS)
        if weights:
            self.weights.update(weights)

    def evaluate(self, board, color: int) -> int:
        score = int(round(_white_perspective(board, self.weights)))
        return score if color == WHITE else -score
