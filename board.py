"""
board.py - 亚马逊棋棋盘数据模型（接口契约 v1.0）

已冻结决策点：
  D1: 一维 list[int]，长度 100，索引 r * BOARD_SIZE + c
  D2: 坐标 (row, col)，row=0 为最上面一行
  D5: 棋盘不可变语义由 rule.apply_move() 保证，本模块只提供纯函数工具

依赖方向：仅标准库，禁止 import 其他项目模块。
"""

# ===== 棋盘状态常量（禁止裸写 0/1/2/3）=====
BOARD_SIZE = 10
CELL_COUNT = BOARD_SIZE * BOARD_SIZE  # 100

EMPTY = 0
BLACK = 1
WHITE = 2
ARROW = 3

# 类型别名：长度 100 的一维列表，board[r * BOARD_SIZE + c]
Board = list[int]


# ====================== 坐标工具 ======================
def idx(r: int, c: int) -> int:
    """(r, c) -> 一维下标"""
    return r * BOARD_SIZE + c


def rc(i: int) -> tuple[int, int]:
    """一维下标 -> (r, c)"""
    return (i // BOARD_SIZE, i % BOARD_SIZE)


def in_bounds(r: int, c: int) -> bool:
    """坐标是否在棋盘内"""
    return 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE


def at(board: Board, r: int, c: int) -> int:
    """取格子内容；越界返回 -1"""
    if not in_bounds(r, c):
        return -1
    return board[idx(r, c)]


# ====================== 棋盘创建与拷贝 ======================
def clone(board: Board) -> Board:
    """浅拷贝一维 list，O(100)。禁止用 copy.deepcopy。"""
    return board[:]


def initial_board() -> Board:
    """
    标准开局（接口契约 v1.0 冻结布局）。
    BLACK: (0,3), (3,0), (6,9), (9,6)
    WHITE: (0,6), (3,9), (6,0), (9,3)
    """
    board = [EMPTY] * CELL_COUNT
    for r, c in [(0, 3), (3, 0), (6, 9), (9, 6)]:
        board[idx(r, c)] = BLACK
    for r, c in [(0, 6), (3, 9), (6, 0), (9, 3)]:
        board[idx(r, c)] = WHITE
    return board


def empty_board() -> Board:
    """全空棋盘（测试与工具用）"""
    return [EMPTY] * CELL_COUNT


# ====================== 统计与渲染 ======================
def count(board: Board, value: int) -> int:
    """统计某类格子数量"""
    return board.count(value)


def to_text(board: Board) -> str:
    """渲染成字符画（调试/演示用）"""
    symbols = {EMPTY: '.', BLACK: 'B', WHITE: 'W', ARROW: 'X'}
    lines = []
    for r in range(BOARD_SIZE):
        row_cells = ' '.join(
            symbols.get(board[idx(r, c)], '?')
            for c in range(BOARD_SIZE)
        )
        lines.append(f"{r:2d} {row_cells}")
    lines.append("   " + " ".join(str(c) for c in range(BOARD_SIZE)))
    return '\n'.join(lines)
