"""控制台随机对局：不依赖 Pygame，用来验证"规则引擎能跑完一局"。

对应 M1 验收标准里的"控制台能跑一局随机对局（不依赖界面）"。

用法（在仓库根目录执行）：
    python tools/random_game.py          # 默认最多走 60 步
    python tools/random_game.py 300      # 指定步数上限

说明：本文件是自检 / 演示工具，不属于任何人的模块交付物，可以随时改。
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

# 允许直接 `python tools/random_game.py` 运行：把仓库根目录加进 import 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from board import BLACK, WHITE, initial_board, to_text  # noqa: E402
from rule import (  # noqa: E402
    BLACK_WIN,
    DRAW,
    WHITE_WIN,
    apply_move,
    game_result,
    legal_moves,
)

RESULT_TEXT = {WHITE_WIN: "白方获胜", BLACK_WIN: "黑方获胜", DRAW: "和棋"}


def main() -> None:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 60

    rng = random.Random()
    board = initial_board()
    color = WHITE  # 题目册：开局位于棋盘下方的玩家先手（本项目约定白方在下）
    step = 0

    print(f"随机对局开始（最多 {limit} 步）")
    while step < limit:
        result = game_result(board)
        if result is not None:
            print(f"\n对局结束：{RESULT_TEXT[result]}（共 {step} 步）")
            break

        moves = legal_moves(board, color)
        move = rng.choice(moves)
        board = apply_move(board, move, color)
        step += 1

        side = "白" if color == WHITE else "黑"
        print(f"[{step:3d}] {side} {move.src} -> {move.dst}   射箭 {move.arrow}")
        color = BLACK if color == WHITE else WHITE
    else:
        print(f"\n达到步数上限 {limit}，对局未结束（引擎工作正常，可加大步数再试）")

    print()
    print(to_text(board))


if __name__ == "__main__":
    main()
