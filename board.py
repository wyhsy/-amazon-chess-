"""棋盘数据模型（接口契约见 docs/interface.md 第 2 节）。

棋盘用一维 `list[int]` 表示，长度 100，索引 = row * 10 + col。
约定：row = 0 是最上面一行，col = 0 是最左列。
（与课程题目册的图示一致；若图示不同，以图示为准并同步更新测试。）

这个模块**只依赖标准库**，不允许 import 项目里其它模块，也不允许 import pygame。
"""

from __future__ import annotations

BOARD_SIZE = 10
CELL_COUNT = BOARD_SIZE * BOARD_SIZE  # 100

# 格子取值：全项目只用这 4 个常量，禁止裸写 0/1/2/3
EMPTY = 0
BLACK = 1
WHITE = 2
ARROW = 3

# 一维棋盘的别名（长度 100）：board[r * BOARD_SIZE + c]
Board = list[int]

# 标准开局：黑 4 枚、白 4 枚（对称分布，测试里固定住）
BLACK_START = ((0, 3), (3, 0), (6, 9), (9, 6))
WHITE_START = ((0, 6), (3, 9), (6, 0), (9, 3))


def idx(r: int, c: int) -> int:
    """(row, col) -> 一维下标。"""
    return r * BOARD_SIZE + c


def rc(i: int) -> tuple:
    """一维下标 -> (row, col)。"""
    return divmod(i, BOARD_SIZE)


def in_bounds(r: int, c: int) -> bool:
    """坐标是否在棋盘内。"""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def at(board: Board, r: int, c: int) -> int:
    """取某格内容；越界返回 -1。"""
    if not in_bounds(r, c):
        return -1
    return board[idx(r, c)]


def clone(board: Board) -> Board:
    """拷贝棋盘。

    一维 list 的浅拷贝是 O(100)，比 copy.deepcopy 快得多——
    AI 搜索每层都要复制棋盘，这里必须是这个写法。
    """
    return board[:]


def initial_board() -> Board:
    """返回标准开局棋盘。"""
    board = [EMPTY] * CELL_COUNT
    for r, c in BLACK_START:
        board[idx(r, c)] = BLACK
    for r, c in WHITE_START:
        board[idx(r, c)] = WHITE
    return board


def empty_board() -> Board:
    """返回全空棋盘（测试与工具脚本用）。"""
    return [EMPTY] * CELL_COUNT


def count(board: Board, value: int) -> int:
    """统计某种格子的数量（测试里断言"棋子不会被吃掉"用）。"""
    return board.count(value)


def to_text(board: Board) -> str:
    """把棋盘渲染成等宽字符画，方便在控制台或测试里肉眼检查。

    `.` = 空、`B` = 黑、`W` = 白、`x` = 箭头（障碍）。
    """
    symbols = {EMPTY: ".", BLACK: "B", WHITE: "W", ARROW: "x"}
    lines = ["    " + " ".join(str(c) for c in range(BOARD_SIZE))]
    for r in range(BOARD_SIZE):
        row = " ".join(symbols.get(board[idx(r, c)], "?") for c in range(BOARD_SIZE))
        lines.append(f"{r:2d}  {row}")
    return "\n".join(lines)
