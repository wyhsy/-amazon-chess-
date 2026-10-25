"""搜索：Minimax + Alpha-Beta + 迭代加深 + 时限控制。

契约（docs/interface.md 第 5 节）：
    search(board, color, depth=2, time_limit=3.0) -> Move | None
    - 返回该方最佳走法；无棋可走时返回 None
    - 超时返回"当前已知最优"（不能卡住界面）

实现要点：
1. 走法用 piece_targets + shot_targets 分步生成，避免一次性构造数千个 Move；
2. negamax 形式 + Alpha-Beta 剪枝，do_move / undo_move 就地回溯（不复制棋盘）；
3. 叶子用 ai_eval.evaluate（正数对当前走棋方有利）；
4. 迭代加深：depth = 1, 2, ... 逐层加深，超时返回上一层已经算完的最优；
5. 时间控制：每 512 个节点检查一次 perf_counter，超时抛 _Timeout；
6. 走法排序 + 候选裁剪：根节点用静态估值排序，内部节点用中心度排序，
   只展开前 candidate_limit 条。开局 2176 条走法，纯 Python 全宽 depth=2
   约 400 万叶节点，3 秒内跑不完；选择性搜索是保证"单步 ≤3 秒"的必要工程手段。

性能基线（本机 Python 3.11，标准开局，粗略值）：
    depth=1（完整排序 2176 条）：约 0.3~0.8 秒
    depth=2 + candidate_limit=32：约 1~3 秒
不同机器会有差异；实际数字记录在 docs/meeting/ 的性能记录里。
"""

from __future__ import annotations

import time

from board import BLACK, BOARD_SIZE, EMPTY, WHITE, idx
from rule import Move, do_move, piece_targets, shot_targets, undo_move
from ai_eval import evaluate

#: 胜负分（远大于估值函数的量级）
MATE = 1_000_000
#: 搜索中的极值
INF = 10**9

#: 难度档位 -> search 参数（ui.py 用 search_by_difficulty 即可，不必自己映射）
DIFFICULTY_SETTINGS = {
    "easy": {"depth": 1, "time_limit": 1.0, "candidate_limit": 24},
    "normal": {"depth": 2, "time_limit": 3.0, "candidate_limit": 32},
    "hard": {"depth": 2, "time_limit": 5.0, "candidate_limit": 64},
}

#: 最近一次 search 的统计（调试 / 性能基线用，不属于接口契约）
last_stats: dict = {}


class _Timeout(Exception):
    """内部用：搜索超出 time_limit。"""


def _other(color: int) -> int:
    """对方颜色。"""
    return BLACK if color == WHITE else WHITE


def _build_center_table() -> list:
    """100 长度的中心度表：中心高、边角低（只用于走法排序，不是估值）。"""
    table = []
    for r in range(BOARD_SIZE):
        for c in range(BOARD_SIZE):
            table.append(10 - int(abs(r - 4.5) + abs(c - 4.5)))
    return table


_CENTER = _build_center_table()


def _move_order_score(move: Move) -> int:
    """纯几何启发式：落点权重高于箭位，越靠中心越优先。"""
    return _CENTER[idx(*move.dst)] * 2 + _CENTER[idx(*move.arrow)]


def _iter_moves(board, color: int):
    """惰性生成该方的完整合法走法（移动 + 射箭）。

    与 rule.legal_moves 的结果一致，但分步生成、不一次性占用几千条走法的内存。
    注意：内部会临时改棋盘来算箭位，但**在 yield 之前一定恢复**，调用方拿到的
    棋盘始终是原始局面。
    """
    for i, value in enumerate(board):
        if value != color:
            continue
        src = divmod(i, BOARD_SIZE)
        for dst in piece_targets(board, *src):
            dst_i = idx(*dst)
            old_src, old_dst = board[i], board[dst_i]
            board[i] = EMPTY
            board[dst_i] = color
            try:
                arrows = shot_targets(board, *dst)
            finally:
                board[i], board[dst_i] = old_src, old_dst
            for arrow in arrows:
                yield Move(src, dst, arrow)


def _order_moves_by_eval(board, color: int, moves: list, deadline, state: dict):
    """根节点排序：对每条走法做一次静态估值，按"对我方有利"降序。

   这是 depth=1 的主要成本（开局约 2176 次 evaluate），也是迭代加深的第一层；
    后续层直接复用这个顺序，不再重复排序。
    超时则提前结束，返回已经评估过的部分（至少保证有走法），并标记 state["truncated"]。
    """
    scored = []
    for i, move in enumerate(moves):
        if deadline is not None and (i & 63) == 0 and time.perf_counter() >= deadline:
            state["truncated"] = True
            break
        old = do_move(board, move, color)
        try:
            score = evaluate(board, color)
        finally:
            undo_move(board, move, color, old)
        scored.append((score, move))
    scored.sort(key=lambda item: item[0], reverse=True)
    return scored


def _negamax(board, color: int, depth: int, alpha: int, beta: int,
             deadline, ply: int, counter: list, candidate_limit: int | None) -> int:
    """negamax：返回当前走棋方 color 视角的分数。"""
    counter[0] += 1
    if deadline is not None and (counter[0] & 511) == 0 and time.perf_counter() >= deadline:
        raise _Timeout

    moves = list(_iter_moves(board, color))
    if not moves:
        # 当前方无路可走 = 当前方输；ply 越大越晚输，分数越高
        return -MATE + ply
    if depth <= 0:
        return evaluate(board, color)

    moves.sort(key=_move_order_score, reverse=True)
    if candidate_limit:
        moves = moves[:candidate_limit]

    best = -INF
    for move in moves:
        old = do_move(board, move, color)
        try:
            score = -_negamax(
                board, _other(color), depth - 1, -beta, -alpha,
                deadline, ply + 1, counter, candidate_limit,
            )
        finally:
            undo_move(board, move, color, old)
        if score > best:
            best = score
        if best > alpha:
            alpha = best
        if alpha >= beta:
            break
    return best


def _search_root(board, color: int, depth: int, deadline,
                 candidate_limit: int | None, counter: list):
    """搜索根节点，返回 (最优走法, 是否完整完成)。

    超时导致排序/根循环提前结束时，第二个返回值为 False；search 只把完整
    完成的层记为已完成深度，避免 last_stats 把"部分搜索"误报成完整搜索。
    """
    moves = list(_iter_moves(board, color))
    if not moves:
        return None, True

    state = {"truncated": False}
    scored = _order_moves_by_eval(board, color, moves, deadline, state)
    if not scored:
        # 时间已经用完：退回任意一条合法走法（绝不返回 None / 非法走法）
        return moves[0], False

    if depth <= 1:
        return scored[0][1], not state["truncated"]

    if candidate_limit:
        scored = scored[:candidate_limit]

    best_move = scored[0][1]
    alpha = -INF
    for _, move in scored:
        if deadline is not None and time.perf_counter() >= deadline:
            state["truncated"] = True
            break
        old = do_move(board, move, color)
        try:
            score = -_negamax(
                board, _other(color), depth - 1, -INF, -alpha,
                deadline, 1, counter, candidate_limit,
            )
        finally:
            undo_move(board, move, color, old)
        if score > alpha:
            alpha = score
            best_move = move
    return best_move, not state["truncated"]


def search(board, color: int, depth: int = 2, time_limit: float | None = 3.0,
           candidate_limit: int | None = 32):
    """返回该方最佳走法；无棋可走返回 None。

    参数：
        board           当前棋盘（不会修改它）
        color           该谁走（board.BLACK / board.WHITE）
        depth           最大搜索深度（迭代加深的层数）
        time_limit      思考时间上限（秒），None 表示不限时
        candidate_limit 每个节点最多展开的候选走法数；默认 32（保证 3 秒内完成），
                        传 None 表示不裁剪（不推荐：开局全宽 depth=2 会超过 3 秒）

    超时保证：即使 time_limit 很小，也返回一条合法走法（不会返回 None、
    不会崩溃）；只有真正无路可走时才返回 None。
    """
    started = time.perf_counter()
    deadline = None if time_limit is None else started + max(0.0, float(time_limit))

    # 先拿一条合法走法做保底（也顺便判断是否无路可走）
    fallback = None
    for move in _iter_moves(board, color):
        fallback = move
        break
    if fallback is None:
        last_stats.clear()
        last_stats.update({
            "depth": 0,
            "nodes": 0,
            "elapsed": time.perf_counter() - started,
            "candidate_limit": candidate_limit,
        })
        return None

    best = fallback
    completed_depth = 0
    counter = [0]

    for d in range(1, max(1, int(depth)) + 1):
        try:
            candidate, finished = _search_root(board, color, d, deadline, candidate_limit, counter)
        except _Timeout:
            break
        if candidate is not None:
            # 第 1 层只要拿到走法就一定有保底；更深层只接受完整完成的结果，
            # 避免把"只搜了一半"的候选当成更强的一层。
            if finished or d == 1:
                best = candidate
            if finished:
                completed_depth = d
        if deadline is not None and time.perf_counter() >= deadline:
            break

    last_stats.clear()
    last_stats.update({
        "depth": completed_depth,
        "nodes": counter[0],
        "elapsed": time.perf_counter() - started,
        "candidate_limit": candidate_limit,
    })
    return best


def search_by_difficulty(board, color: int, difficulty: str = "normal"):
    """按难度档位调用 search；ui.py 直接调这个函数即可。"""
    settings = DIFFICULTY_SETTINGS.get(difficulty, DIFFICULTY_SETTINGS["normal"])
    return search(board, color, **settings)
