"""程序入口。

契约（docs/interface.md 第 5 节）：
    python main.py --mode pvp|pve --difficulty easy|normal|hard

用法示例：
    python main.py                          # 默认：人机对战、普通难度、执白
    python main.py --mode pvp               # 人人对战
    python main.py --mode pve --difficulty hard
    python main.py --color black            # 执黑（白方先手）

TODO(@wyhsy)：界面交互完成前，如果想快速验证规则/搜索，可以先跑控制台版：
    python tools/random_game.py 200
"""

from __future__ import annotations

import argparse

from board import BLACK, WHITE
from ui import GameUI


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="亚马逊棋（人机博弈课程设计）")
    parser.add_argument(
        "--mode",
        choices=["pvp", "pve"],
        default="pve",
        help="pvp = 人人对战；pve = 人机对战（默认）",
    )
    parser.add_argument(
        "--difficulty",
        choices=["easy", "normal", "hard"],
        default="normal",
        help="AI 难度（影响搜索深度/时限）",
    )
    parser.add_argument(
        "--color",
        choices=["white", "black"],
        default="white",
        help="人类玩家执哪一方（白方先手）",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    human_color = WHITE if args.color == "white" else BLACK

    ui = GameUI(mode=args.mode, human_color=human_color, difficulty=args.difficulty)
    ui.run()


if __name__ == "__main__":
    main()
