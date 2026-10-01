"""
rule.py - 亚马逊棋规则引擎（接口契约 v1.0）

已冻结决策点：
  D3: Move = namedtuple("Move", "src dst arrow")，三个元素都是 (row, col)
  D4: 双粒度走法生成 — legal_moves() 一次性生成全部；piece_targets()/shot_targets() 分步
  D5: apply_move() 返回新棋盘（不可变）；do_move()/undo_move() 就地回溯（AI 内部用）

依赖方向：仅 import board，禁止 import pygame / ui / ai_*。
"""
from collections import namedtuple

from board import (
    Board, BOARD_SIZE, EMPTY, BLACK, WHITE, ARROW,
    idx, in_bounds, at, clone,
)

# ===== 胜负常量 =====
WHITE_WIN = 1
BLACK_WIN = -1
DRAW = 0

# ===== 走法结构 =====
Move = namedtuple("Move", "src dst arrow")
# src, dst, arrow 都是 (row, col)

# 皇后走法 8 方向
_DIRECTIONS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1),           (0, 1),
    (1, -1),  (1, 0),  (1, 1),
]


# ====================== 内部工具 ======================
def _targets(board: Board, r: int, c: int) -> list[tuple[int, int]]:
    """
    从 (r,c) 出发，沿 8 方向所有可达空位。
    棋子移动和射箭规则完全相同，共用此函数。
    """
    result = []
    for dr, dc in _DIRECTIONS:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc) and at(board, nr, nc) == EMPTY:
            result.append((nr, nc))
            nr += dr
            nc += dc
    return result


def _path_clear(board: Board, r1: int, c1: int, r2: int, c2: int) -> bool:
    """检查 (r1,c1) 到 (r2,c2) 的直线路径是否通畅（不含起点，检查到终点前一格）。"""
    if r1 == r2 and c1 == c2:
        return False
    dr = 1 if r2 > r1 else (-1 if r2 < r1 else 0)
    dc = 1 if c2 > c1 else (-1 if c2 < c1 else 0)
    # 必须是直线：同行、同列、或对角线
    if dr != 0 and dc != 0 and abs(r2 - r1) != abs(c2 - c1):
        return False
    r, c = r1 + dr, c1 + dc
    while (r, c) != (r2, c2):
        if at(board, r, c) != EMPTY:
            return False
        r += dr
        c += dc
    return True


# ====================== 分步走法生成（D4）======================
def piece_targets(board: Board, r: int, c: int) -> list[tuple[int, int]]:
    """单个棋子的可移动目标格（皇后 8 方向直线），不包含射箭。"""
    if at(board, r, c) not in (BLACK, WHITE):
        return []
    return _targets(board, r, c)


def shot_targets(board: Board, r: int, c: int) -> list[tuple[int, int]]:
    """从 (r,c) 射箭的可选落点（规则与移动完全相同：皇后 8 方向直线）。"""
    return _targets(board, r, c)


# ====================== 一次性走法生成（D4）======================
def legal_moves(board: Board, color: int) -> list[Move]:
    """
    生成该方全部合法完整走法（移动 + 射箭）。
    开局量级为数千条，注意性能。
    """
    moves = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if at(board, r, c) != color:
                continue
            for dst in piece_targets(board, r, c):
                # 临时移动棋子，计算射箭落点
                src_i = idx(r, c)
                dst_i = idx(dst[0], dst[1])
                board[src_i] = EMPTY
                board[dst_i] = color
                for arrow in shot_targets(board, dst[0], dst[1]):
                    moves.append(Move(src=(r, c), dst=dst, arrow=arrow))
                # 恢复临时状态
                board[src_i] = color
                board[dst_i] = EMPTY
    return moves


# ====================== 合法性校验 ======================
def is_legal(board: Board, move: Move, color: int) -> bool:
    """校验一条完整走法是否合法（供 UI 与测试使用）。"""
    src_r, src_c = move.src
    dst_r, dst_c = move.dst
    arr_r, arr_c = move.arrow

    # 1. 起点必须是己方棋子
    if at(board, src_r, src_c) != color:
        return False
    # 2. 终点必须是空位
    if at(board, dst_r, dst_c) != EMPTY:
        return False
    # 3. 移动路径必须通畅
    if not _path_clear(board, src_r, src_c, dst_r, dst_c):
        return False
    # 4. 射箭落点必须是空位（移动后原位置已空，可射回）
    if at(board, arr_r, arr_c) != EMPTY and (arr_r, arr_c) != (src_r, src_c):
        return False
    # 5. 箭不能射到棋子移动后的所在格
    if (arr_r, arr_c) == (dst_r, dst_c):
        return False
    # 6. 射箭路径通畅（临时模拟移动后校验）
    src_i = idx(src_r, src_c)
    dst_i = idx(dst_r, dst_c)
    old_src, old_dst = board[src_i], board[dst_i]
    board[src_i] = EMPTY
    board[dst_i] = color
    valid = _path_clear(board, dst_r, dst_c, arr_r, arr_c)
    board[src_i] = old_src
    board[dst_i] = old_dst
    return valid


# ====================== 不可变执行（D5）======================
def apply_move(board: Board, move: Move, color: int) -> Board:
    """返回走完后的新棋盘，不修改入参 board（不可变语义）。"""
    new_board = clone(board)
    src_i = idx(move.src[0], move.src[1])
    dst_i = idx(move.dst[0], move.dst[1])
    arr_i = idx(move.arrow[0], move.arrow[1])
    new_board[src_i] = EMPTY
    new_board[dst_i] = color
    new_board[arr_i] = ARROW
    return new_board


# ====================== 就地回溯（D5，AI 内部用）======================
def do_move(board: Board, move: Move, color: int) -> tuple:
    """
    就地执行走法，返回被覆盖格子的旧值 (old_src, old_dst, old_arrow)。
    供 AI 搜索回溯使用，仅 AI 内部调用。
    """
    src_i = idx(move.src[0], move.src[1])
    dst_i = idx(move.dst[0], move.dst[1])
    arr_i = idx(move.arrow[0], move.arrow[1])
    old = (board[src_i], board[dst_i], board[arr_i])
    board[src_i] = EMPTY
    board[dst_i] = color
    board[arr_i] = ARROW
    return old


def undo_move(board: Board, move: Move, color: int, old: tuple) -> None:
    """与 do_move 配对，恢复棋盘。color 参数保留以匹配接口签名。"""
    src_i = idx(move.src[0], move.src[1])
    dst_i = idx(move.dst[0], move.dst[1])
    arr_i = idx(move.arrow[0], move.arrow[1])
    board[src_i], board[dst_i], board[arr_i] = old


# ====================== 终局判定 ======================
def has_any_move(board: Board, color: int) -> bool:
    """
    该方是否还有棋可走（用于终局判定，应比 legal_moves 早退更高效）。
    只要有一枚棋子能移动，就有棋可走。
    """
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            if at(board, r, c) == color:
                if piece_targets(board, r, c):
                    return True
    return False


def game_result(board: Board) -> int | None:
    """
    None=未结束；DRAW=和棋；WHITE_WIN / BLACK_WIN=已分胜负。
    规则：该方 has_any_move 为 False 时该方判负；双方都无法走子为和棋。
    """
    black_can = has_any_move(board, BLACK)
    white_can = has_any_move(board, WHITE)
    if not black_can and not white_can:
        return DRAW
    if not black_can:
        return WHITE_WIN
    if not white_can:
        return BLACK_WIN
    return None


# ====================== 领地计算（仅供估值/显示，不判胜负）======================
def territory(board: Board) -> tuple[int, int]:
    """
    (黑方领地, 白方领地)：每枚棋子 8 方向紧邻空格各记 1 分。
    只作估值特征与界面显示用，不判定胜负。
    """
    black_territory = 0
    white_territory = 0
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            cell = at(board, r, c)
            if cell not in (BLACK, WHITE):
                continue
            for dr, dc in _DIRECTIONS:
                nr, nc = r + dr, c + dc
                if in_bounds(nr, nc) and at(board, nr, nc) == EMPTY:
                    if cell == BLACK:
                        black_territory += 1
                    else:
                        white_territory += 1
    return (black_territory, white_territory)
