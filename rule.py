"""
rule.py - 亚马逊棋规则引擎
职责：皇后移动/射箭合法性判断、枚举全部合法完整走法、游戏结束判定、执行/撤销走法
所有方法为静态方法，第一个参数接收 AmazonsBoard 对象，本身不持有棋盘状态。

接口契约：
  - 所有方法不修改 board，除非显式调用 apply_move / undo_move
  - apply_move 会同步维护 board.black_pieces / white_pieces 缓存
  - 走法字典格式：{"from_x","from_y","to_x","to_y","arrow_x","arrow_y"}
"""
from board import AmazonsBoard


class AmazonsRule:
    """亚马逊棋规则引擎：无状态，所有方法接收 board 对象。"""

    # 皇后走法 8 方向向量（棋子移动和箭飞行共用）
    _DIRECTIONS = [
        (-1, 0), (1, 0), (0, -1), (0, 1),
        (-1, -1), (-1, 1), (1, -1), (1, 1)
    ]

    # ====================== 内部工具 ======================
    @staticmethod
    def _is_path_clear(board: AmazonsBoard, sx, sy, ex, ey) -> bool:
        """
        检查 (sx,sy) 到 (ex,ey) 的直线路径是否完全通畅（不含起点，含终点前一格）。
        【修复】补充直线性校验：非横/竖/斜的走法直接返回 False，避免异常坐标导致死循环或越界。
        """
        if sx == ex and sy == ey:
            return False
        # 必须是直线：同行、同列、或对角线（横纵距离相等）
        if sx != ex and sy != ey and abs(ex - sx) != abs(ey - sy):
            return False
        dx = 1 if ex > sx else (-1 if ex < sx else 0)
        dy = 1 if ey > sy else (-1 if ey < sy else 0)
        x, y = sx + dx, sy + dy
        while x != ex or y != ey:
            if board.board[y][x] != board.EMPTY:
                return False
            x += dx
            y += dy
        return True

    @staticmethod
    def _get_all_targets(board: AmazonsBoard, x, y) -> list:
        """
        从 (x,y) 出发，沿 8 方向所有可达空位坐标。
        同时用于计算棋子移动终点和箭的合法落点。
        """
        targets = []
        for dx, dy in AmazonsRule._DIRECTIONS:
            nx, ny = x + dx, y + dy
            while board.is_in_board(nx, ny) and board.board[ny][nx] == board.EMPTY:
                targets.append((nx, ny))
                nx += dx
                ny += dy
        return targets

    # ====================== 合法性判断 ======================
    @staticmethod
    def is_valid_move(board: AmazonsBoard, sx, sy, ex, ey) -> bool:
        """
        判断棋子从 (sx,sy) 移动到 (ex,ey) 是否合法。
        规则：起点是当前玩家棋子 + 终点是空位 + 路径通畅。
        """
        if not board.is_in_board(sx, sy) or not board.is_in_board(ex, ey):
            return False
        if board.board[sy][sx] != board.current_player:
            return False
        if board.board[ey][ex] != board.EMPTY:
            return False
        return AmazonsRule._is_path_clear(board, sx, sy, ex, ey)

    @staticmethod
    def is_valid_arrow(board: AmazonsBoard, x, y, ax, ay) -> bool:
        """
        判断从 (x,y) 射箭到 (ax,ay) 是否合法。
        规则：起点是当前玩家棋子 + 落点是空位 + 不能原地射 + 路径通畅。
        """
        if not board.is_in_board(x, y) or not board.is_in_board(ax, ay):
            return False
        if board.board[y][x] != board.current_player:
            return False
        if board.board[ay][ax] != board.EMPTY:
            return False
        if x == ax and y == ay:
            return False
        return AmazonsRule._is_path_clear(board, x, y, ax, ay)

    # ====================== 枚举全部合法走法 ======================
    @staticmethod
    def generate_all_legal_moves(board: AmazonsBoard) -> list:
        """
        生成当前玩家所有合法的完整回合动作（移动 + 射箭）。
        :return: 走法列表，每项为 {"from_x","from_y","to_x","to_y","arrow_x","arrow_y"}
        """
        moves = []
        player = board.current_player
        pieces = board.black_pieces if player == board.BLACK else board.white_pieces

        for (x, y) in pieces:
            move_targets = AmazonsRule._get_all_targets(board, x, y)
            for (to_x, to_y) in move_targets:
                # 临时模拟移动，计算射箭落点
                board.board[y][x] = board.EMPTY
                board.board[to_y][to_x] = player
                arrow_targets = AmazonsRule._get_all_targets(board, to_x, to_y)
                for (ax, ay) in arrow_targets:
                    moves.append({
                        "from_x": x, "from_y": y,
                        "to_x": to_x, "to_y": to_y,
                        "arrow_x": ax, "arrow_y": ay
                    })
                # 恢复临时状态
                board.board[to_y][to_x] = board.EMPTY
                board.board[y][x] = player

        return moves

    # ====================== 游戏结束判定 ======================
    @staticmethod
    def has_no_legal_moves(board: AmazonsBoard, player: int) -> bool:
        """
        判断指定玩家是否无棋可走。
        只要有一枚棋子能移动，回合就能继续（移动后原位置必为空，箭可射回）。
        """
        pieces = board.black_pieces if player == board.BLACK else board.white_pieces
        for (x, y) in pieces:
            if len(AmazonsRule._get_all_targets(board, x, y)) > 0:
                return False
        return True

    @staticmethod
    def check_game_over(board: AmazonsBoard):
        """
        检查游戏是否结束。
        :return: 未结束返回 None；结束返回 {"winner": 获胜方, "loser": 失败方}
        """
        if AmazonsRule.has_no_legal_moves(board, board.current_player):
            loser = board.current_player
            winner = board.WHITE if loser == board.BLACK else board.BLACK
            return {"winner": winner, "loser": loser}
        return None

    # ====================== 执行与撤销 ======================
    @staticmethod
    def apply_move(board: AmazonsBoard, move: dict):
        """
        执行一个完整回合动作（移动棋子 + 射箭 + 切换玩家）。
        执行前自动保存状态，支持 undo。
        :param move: {"from_x","from_y","to_x","to_y","arrow_x","arrow_y"}
        :raises ValueError: 走法非法或缓存不一致时抛出，拒绝执行且不污染状态
        """
        from_pos = (move["from_x"], move["from_y"])
        cache = board.black_pieces if board.current_player == board.BLACK else board.white_pieces

        # 前置校验 1：缓存与棋盘一致
        if from_pos not in cache:
            raise ValueError(f"棋子缓存与棋盘状态不一致：{from_pos} 不在缓存中")

        # 前置校验 2：移动合法
        if not AmazonsRule.is_valid_move(board, move["from_x"], move["from_y"],
                                         move["to_x"], move["to_y"]):
            raise ValueError(f"非法移动：({move['from_x']},{move['from_y']}) → "
                             f"({move['to_x']},{move['to_y']})")

        # 前置校验 3：射箭合法（临时模拟移动后校验）
        board.board[move["from_y"]][move["from_x"]] = board.EMPTY
        board.board[move["to_y"]][move["to_x"]] = board.current_player
        valid_arrow = AmazonsRule.is_valid_arrow(board, move["to_x"], move["to_y"],
                                                 move["arrow_x"], move["arrow_y"])
        board.board[move["to_y"]][move["to_x"]] = board.EMPTY
        board.board[move["from_y"]][move["from_x"]] = board.current_player

        if not valid_arrow:
            raise ValueError(f"非法射箭：({move['to_x']},{move['to_y']}) 射向 "
                             f"({move['arrow_x']},{move['arrow_y']})")

        # ===== 正式执行 =====
        board.save_state()

        # 1. 移动棋子
        board.board[move["from_y"]][move["from_x"]] = board.EMPTY
        board.board[move["to_y"]][move["to_x"]] = board.current_player

        # 2. 同步棋子位置缓存
        if board.current_player == board.BLACK:
            board.black_pieces.remove(from_pos)
            board.black_pieces.append((move["to_x"], move["to_y"]))
        else:
            board.white_pieces.remove(from_pos)
            board.white_pieces.append((move["to_x"], move["to_y"]))

        # 3. 放置障碍
        board.board[move["arrow_y"]][move["arrow_x"]] = board.OBSTACLE

        # 4. 切换玩家
        board.current_player = board.WHITE if board.current_player == board.BLACK else board.BLACK

    @staticmethod
    def undo_move(board: AmazonsBoard) -> bool:
        """
        撤销上一步走法，恢复棋盘状态和当前玩家。
        :return: 撤销成功返回 True；历史栈为空返回 False
        """
        return board.restore_state()

