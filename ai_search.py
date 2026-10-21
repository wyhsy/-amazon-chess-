"""搜索（M2 阶段骨架：先跑通，M3 再上 Minimax + Alpha-Beta）。

契约（docs/interface.md 第 5 节）：
    search(board, color, depth=2, time_limit=3.0) -> Move | None
    - 返回该方最佳走法；无棋可走时返回 None
    - 超时返回"当前已知最优"（不能卡住界面）

当前实现：**随机挑一条合法走法**。
    目的：让 main.py / ui.py 的"人机对战"通路先跑通，M2 就能看到 AI 走棋。

TODO(@wyhsy —— 见 docs/tasks/M1-任务派发.md 任务卡 4)：
    1. 把 _pick_random_move 换成 Minimax + Alpha-Beta 剪枝
    2. 用 rule.piece_targets / shot_targets 分步生成走法，配合走法排序提升剪枝效率
    3. 用 ai_eval.evaluate 作为叶子节点估值（注意：它返回的是"对 color 有利为正"）
    4. 用 do_move / undo_move 做就地回溯，避免每层复制棋盘
    5. 实现 time_limit：超过时限就返回当前最优（迭代加深最方便）
"""

from __future__ import annotations

import random

from rule import legal_moves

#: 搜索用的随机数发生器（单独实例，方便测试时复现）
_rng = random.Random()


def _pick_random_move(moves: list) -> object:
    """TODO(@wyhsy)：M3 换成 Minimax 搜索结果。"""
    return _rng.choice(moves) if moves else None


def search(board, color: int, depth: int = 2, time_limit: float | None = 3.0):
    """返回该方最佳走法；无棋可走返回 None。

    参数：
        board       当前棋盘（不要修改它）
        color       该谁走（board.BLACK / board.WHITE）
        depth       搜索深度（M3 才会真正用到）
        time_limit  思考时间上限（秒），None 表示不限时
    """
    moves = legal_moves(board, color)
    if not moves:
        return None

    # TODO(@wyhsy): 用 Minimax + Alpha-Beta 替换下面这行
    return _pick_random_move(moves)
