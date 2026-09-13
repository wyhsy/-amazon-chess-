"""规则引擎：走法生成、合法性校验、终局判定。

规则要点（取自课程题目册《亚马逊棋博弈项目规则简表》）：
1. 一步棋 = 先移动一个己方亚马逊，再从落点射一支箭；两段都必须走"皇后路线"
   （8 个方向横竖斜任意距离），路径上不能有棋子或箭头。
2. 棋子与箭头占的格子不可通过、不可落子；箭头一旦放下永不消失。
3. 该方一个合法走法都没有 → 该方判负；双方都无路可走 → 和棋。
4. 全程不能吃掉任何棋子（己方或对方）。

重要：题目册只规定"行棋方法与皇后相同"，**没有马步 / 骑士走法**。
若老师后来要求加入马步，只需在 DIRECTIONS 之外再补一组骑士偏移，
其余函数（候选格检查、射箭、终局判定）都不用改。

本模块不允许 import pygame，也不允许 import ui/ai_*，保证能在无图形环境的 CI 里测试。
"""

from __future__ import annotations

from collections import namedtuple

from board import ARROW, BLACK, EMPTY, WHITE, Board, idx, in_bounds, rc

#: 一步走法：(起点, 落点, 射箭位置)，三个元素都是 (row, col)
Move = namedtuple("Move", "src dst arrow")

#: 终局结果常量
WHITE_WIN = 1
BLACK_WIN = -1
DRAW = 0

#: 皇后的 8 个行进方向：(行增量, 列增量)
DIRECTIONS = (
    (1, 0), (-1, 0), (0, 1), (0, -1),
    (1, 1), (1, -1), (-1, 1), (-1, -1),
)


def _iter_pieces(board: Board, color: int):
    """产出该方每枚棋子的 (row, col)。内部辅助函数。"""
    for i, v in enumerate(board):
        if v == color:
            yield rc(i)


def piece_targets(board: Board, r: int, c: int) -> list:
    """(r, c) 处棋子的可移动目标格（皇后 8 方向直线，遇到任何占用就停）。"""
    targets = []
    for dr, dc in DIRECTIONS:
        nr, nc = r + dr, c + dc
        while in_bounds(nr, nc):
            if board[idx(nr, nc)] != EMPTY:
                break
            targets.append((nr, nc))
            nr += dr
            nc += dc
    return targets


def shot_targets(board: Board, r: int, c: int) -> list:
    """从 (r, c) 射箭的可选落点：规则与棋子移动完全相同。"""
    return piece_targets(board, r, c)


def legal_moves(board: Board, color: int) -> list:
    """生成该方全部合法走法（"移动 + 射箭"的完整组合）。

    开局量级在数千条。主要给界面和测试用；
    AI 搜索请改用 piece_targets() + shot_targets() 分步生成，以便边生成边剪枝。
    """
    moves = []
    for src_r, src_c in _iter_pieces(board, color):
        for dst_r, dst_c in piece_targets(board, src_r, src_c):
            # 临时构造"移动之后"的棋盘，再用它算可选箭位（一维数组拷贝很便宜）
            moved = board[:]
            moved[idx(src_r, src_c)] = EMPTY
            moved[idx(dst_r, dst_c)] = color
            for arrow_r, arrow_c in piece_targets(moved, dst_r, dst_c):
                moves.append(
                    Move((src_r, src_c), (dst_r, dst_c), (arrow_r, arrow_c))
                )
    return moves


def is_legal(board: Board, move: Move, color: int) -> bool:
    """校验一条完整走法在当前局面下是否合法（供界面与测试使用）。"""
    src, dst, arrow = move
    src_r, src_c = src
    if not in_bounds(src_r, src_c) or board[idx(src_r, src_c)] != color:
        return False
    if dst not in piece_targets(board, src_r, src_c):
        return False

    dst_r, dst_c = dst
    moved = board[:]
    moved[idx(src_r, src_c)] = EMPTY
    moved[idx(dst_r, dst_c)] = color
    return arrow in piece_targets(moved, dst_r, dst_c)


def apply_move(board: Board, move: Move, color: int) -> Board:
    """返回走完这一步之后的新棋盘，**不修改入参 board**。"""
    src, dst, arrow = move
    new_board = board[:]
    new_board[idx(*src)] = EMPTY
    new_board[idx(*dst)] = color
    new_board[idx(*arrow)] = ARROW
    return new_board


def do_move(board: Board, move: Move, color: int) -> tuple:
    """就地执行走法（AI 搜索用），返回 (起点旧值, 落点旧值)，配合 undo_move 复原。"""
    src, dst, arrow = move
    src_i, dst_i = idx(*src), idx(*dst)
    old = (board[src_i], board[dst_i])
    board[src_i] = EMPTY
    board[dst_i] = color
    board[idx(*arrow)] = ARROW
    return old


def undo_move(board: Board, move: Move, color: int, old: tuple) -> None:
    """与 do_move 配对，把棋盘完全恢复成调用之前的样子。

    color 在这里用不到，保留它只是为了和 do_move 的签名对称、将来便于加校验。
    """
    src, dst, arrow = move
    board[idx(*arrow)] = EMPTY
    board[idx(*dst)] = old[1]
    board[idx(*src)] = old[0]


def has_any_move(board: Board, color: int) -> bool:
    """该方是否还有棋可走（终局判定专用，比 legal_moves 快得多）。

    为什么只检查"棋子能不能移动"就够了（不用再看能不能射箭）：
    如果某枚棋子能从 A 走到 B，说明 A→B 路径上的格子本来是空的，而且 A 移开后也空，
    那么"把箭射回 A"一定合法。所以
        「存在可移动的棋子」⟺「存在合法的完整走法」。
    """
    for r, c in _iter_pieces(board, color):
        if piece_targets(board, r, c):
            return True
    return False


def territory(board: Board) -> tuple:
    """返回 (黑方领地, 白方领地)：每枚棋子 8 个方向上紧邻的空格各记 1 分。

    说明：
    - 同一个空格可能被两枚棋子同时计入，这是亚马逊棋常见的领地计法；
    - 本函数只提供数据（给估值函数当特征、给界面显示用），
      **不用于判定胜负** —— 题目册只规定"无路可走判负 / 双方无路为和棋"。
    """
    counts = {BLACK: 0, WHITE: 0}
    for i, v in enumerate(board):
        if v != BLACK and v != WHITE:
            continue
        r, c = rc(i)
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if in_bounds(nr, nc) and board[idx(nr, nc)] == EMPTY:
                counts[v] += 1
    return counts[BLACK], counts[WHITE]


def game_result(board: Board) -> int | None:
    """判定局面结果：None = 未结束；DRAW = 双方都无路可走；WHITE_WIN / BLACK_WIN。"""
    white_can = has_any_move(board, WHITE)
    black_can = has_any_move(board, BLACK)
    if not white_can and not black_can:
        return DRAW
    if not white_can:
        return BLACK_WIN
    if not black_can:
        return WHITE_WIN
    return None
