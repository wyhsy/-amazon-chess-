"""Pygame 界面（M2 阶段骨架）。

依赖方向（见 docs/interface.md 第 6 节）：
    ui 可以 import board / rule / ai_search，**禁止 import ai_eval**。

已完成（可以直接跑起来看到画面）：
    - 窗口、10×10 棋盘网格、坐标标注
    - 开局棋子绘制、箭头绘制
    - 点击选中高亮（只是高亮，还没有走棋逻辑）
    - 底部状态栏

TODO（@guoyi1005 —— 见 docs/tasks/M1-任务派发.md 任务卡 2）：
    1. 两段式操作状态机：选中棋子 → 选落点 → 选射箭位置 → 落子
       建议用 self.selected / self.pending_move 两个字段记录中间状态
    2. 非法操作提示（点到障碍、路径被挡、选错颜色）—— 不要崩，给个提示即可
    3. 胜负提示（用 rule.game_result 判断）与"再来一局"
    4. 人机模式下显示"AI 思考中…"并把界面卡顿处理好
    5. 走法提示（可选）：选中棋子后用半透明格标出 piece_targets

注意：本文件 import 了 pygame，所以**测试代码不要 import ui**（CI 里没有显示器）。
"""

from __future__ import annotations

import pygame

from board import ARROW, BLACK, BOARD_SIZE, EMPTY, WHITE, at, initial_board
from rule import is_legal, legal_moves  # noqa: F401  TODO 阶段会用到，现在先导入

CELL = 60
MARGIN = 40
STATUS_H = 40

# 配色
COLOR_BG = (30, 30, 34)
COLOR_LIGHT = (238, 238, 210)
COLOR_DARK = (118, 150, 86)
COLOR_BLACK_PIECE = (32, 32, 36)
COLOR_WHITE_PIECE = (250, 250, 250)
COLOR_ARROW = (200, 60, 60)
COLOR_SELECT = (255, 205, 0)
COLOR_GRID = (70, 70, 76)
COLOR_STATUS = (235, 235, 235)


class GameUI:
    """亚马逊棋界面。

    契约（docs/interface.md 第 5 节）：
        GameUI(mode="pve", human_color=WHITE, difficulty="normal")
        GameUI.run() 进入主循环，阻塞直到退出。
    """

    def __init__(self, mode: str = "pve", human_color: int = WHITE, difficulty: str = "normal") -> None:
        self.mode = mode
        self.human_color = human_color
        self.difficulty = difficulty

        self.board = initial_board()
        self.turn = WHITE           # 白方先手（题目册：棋盘下方玩家先手）
        self.selected = None        # 当前选中的棋子坐标 (r, c)
        self.pending_move = None    # TODO(@guoyi1005): 已选好落点、等待选箭位
        self.message = ""           # 状态栏提示（非法操作提示可以写这里）
        self.running = True

        pygame.init()
        size = BOARD_SIZE * CELL + MARGIN * 2
        self.screen = pygame.display.set_mode((size, size + STATUS_H))
        pygame.display.set_caption("亚马逊棋")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("microsoftyahei,simhei,arial", 18)

    # ------------------------------------------------------------------ 坐标换算

    def cell_to_xy(self, r: int, c: int) -> tuple[int, int]:
        """棋盘坐标 -> 屏幕像素左上角。"""
        return MARGIN + c * CELL, MARGIN + r * CELL

    def xy_to_cell(self, x: int, y: int):
        """屏幕像素 -> 棋盘坐标；点在棋盘外返回 None。"""
        c = (x - MARGIN) // CELL
        r = (y - MARGIN) // CELL
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            return int(r), int(c)
        return None

    # ------------------------------------------------------------------ 绘制

    def draw_board(self) -> None:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                x, y = self.cell_to_xy(r, c)
                color = COLOR_LIGHT if (r + c) % 2 == 0 else COLOR_DARK
                pygame.draw.rect(self.screen, color, (x, y, CELL, CELL))

        # 网格线
        end = MARGIN + BOARD_SIZE * CELL
        for i in range(BOARD_SIZE + 1):
            pos = MARGIN + i * CELL
            pygame.draw.line(self.screen, COLOR_GRID, (pos, MARGIN), (pos, end), 1)
            pygame.draw.line(self.screen, COLOR_GRID, (MARGIN, pos), (end, pos), 1)

    def draw_pieces(self) -> None:
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                value = at(self.board, r, c)
                if value == EMPTY:
                    continue
                x, y = self.cell_to_xy(r, c)
                center = (x + CELL // 2, y + CELL // 2)
                if value == ARROW:
                    pygame.draw.circle(self.screen, COLOR_ARROW, center, CELL // 5)
                else:
                    fill = COLOR_BLACK_PIECE if value == BLACK else COLOR_WHITE_PIECE
                    pygame.draw.circle(self.screen, fill, center, CELL // 2 - 8)
                    pygame.draw.circle(self.screen, COLOR_GRID, center, CELL // 2 - 8, 2)

    def draw_selection(self) -> None:
        if self.selected is not None:
            r, c = self.selected
            x, y = self.cell_to_xy(r, c)
            pygame.draw.rect(self.screen, COLOR_SELECT, (x, y, CELL, CELL), 4)

    def draw_status(self) -> None:
        side = "白方" if self.turn == WHITE else "黑方"
        text = f"{side}走棋 | 模式 {self.mode} | 难度 {self.difficulty}"
        if self.message:
            text = f"{text} | {self.message}"
        surface = self.font.render(text, True, COLOR_STATUS)
        self.screen.blit(surface, (MARGIN, MARGIN + BOARD_SIZE * CELL + 10))

    # ------------------------------------------------------------------ 事件

    def handle_click(self, pos: tuple[int, int]) -> None:
        """鼠标左键点击。

        TODO(@guoyi1005)：把这里换成完整的两段式操作状态机：
            1) 没有选中棋子时：点己方棋子 → self.selected = (r, c)
            2) 已选中棋子时：点合法落点 → self.pending_move = (src, dst)
            3) 已有 pending_move 时：点合法箭位 → apply_move + 切换 self.turn

        判断合法性请使用 rule.legal_moves / rule.is_legal，不要自己重写规则。
        现在只做"选中高亮"，方便你先把画面跑起来。
        """
        cell = self.xy_to_cell(*pos)
        if cell is None:
            return
        self.selected = cell

    # ------------------------------------------------------------------ 主循环

    def run(self) -> None:
        """进入主循环，阻塞直到窗口关闭。"""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    self.handle_click(event.pos)

            self.screen.fill(COLOR_BG)
            self.draw_board()
            self.draw_selection()
            self.draw_pieces()
            self.draw_status()
            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    # 方便单独调试界面：python ui.py
    GameUI(mode="pvp").run()
