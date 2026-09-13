"""
board.py - 亚马逊棋棋盘数据模型
职责：棋盘表示、初始化、状态保存/恢复、坐标工具、棋子位置缓存
本模块只负责数据存储，不包含任何规则判定逻辑。
规则判定请使用 rule.py 中的 AmazonsRule。

对外接口（供 rule.py / ai_search.py / ui.py 调用）：
  - board.board          : 10x10 二维数组，值为 EMPTY/BLACK/WHITE/OBSTACLE
  - board.current_player : 当前执子方（BLACK 或 WHITE）
  - board.black_pieces   : 黑方棋子坐标列表 [(x,y), ...]
  - board.white_pieces   : 白方棋子坐标列表 [(x,y), ...]
  - board.history        : 历史状态栈（供 undo）
  - board.init_standard() / clone() / save_state() / restore_state()
  - board.is_in_board(x, y) / get_piece_positions(player)
"""
from copy import deepcopy


class AmazonsBoard:
    """棋盘数据模型：仅维护状态，不做规则判定。"""

    # ===== 棋盘状态常量 =====
    EMPTY = 0       # 空位
    BLACK = 1       # 黑方棋子
    WHITE = 2       # 白方棋子
    OBSTACLE = 3    # 永久障碍
    BOARD_SIZE = 10 # 标准棋盘 10x10

    def __init__(self):
        """创建空棋盘框架（未摆棋子），调用 init_standard() 后才可使用。"""
        self.board = []
        self.current_player = self.BLACK  # 黑方先手
        self.history = []                 # 历史状态栈
        self.black_pieces = []            # 黑方棋子位置缓存
        self.white_pieces = []            # 白方棋子位置缓存

    # ====================== 初始化与拷贝 ======================
    def init_standard(self):
        """初始化标准 10x10 开局：双方各 4 枚棋子，黑方下方先行。"""
        self.board = [[self.EMPTY for _ in range(self.BOARD_SIZE)]
                      for _ in range(self.BOARD_SIZE)]

        # 白方（上方）
        self.board[0][3] = self.WHITE
        self.board[0][6] = self.WHITE
        self.board[3][0] = self.WHITE
        self.board[3][9] = self.WHITE

        # 黑方（下方）
        self.board[6][0] = self.BLACK
        self.board[6][9] = self.BLACK
        self.board[9][3] = self.BLACK
        self.board[9][6] = self.BLACK

        # 棋子位置缓存（坐标为 (x, y)）
        self.black_pieces = [(0, 6), (9, 6), (3, 9), (6, 9)]
        self.white_pieces = [(3, 0), (6, 0), (0, 3), (9, 3)]

        self.current_player = self.BLACK
        self.history.clear()

    def clone(self):
        """深拷贝当前棋盘，返回完全独立的新实例（用于 AI 前瞻搜索）。"""
        new_board = AmazonsBoard()
        new_board.board = deepcopy(self.board)
        new_board.current_player = self.current_player
        new_board.black_pieces = self.black_pieces.copy()
        new_board.white_pieces = self.white_pieces.copy()
        # 不复制 history：新实例用于独立搜索分支
        return new_board

    # ====================== 状态保存与恢复 ======================
    def save_state(self):
        """保存当前完整状态到历史栈（apply_move 前自动调用）。"""
        self.history.append({
            "board": deepcopy(self.board),
            "current_player": self.current_player,
            "black_pieces": self.black_pieces.copy(),
            "white_pieces": self.white_pieces.copy()
        })

    def restore_state(self):
        """
        从历史栈弹出并恢复上一步状态。
        :return: 恢复成功返回 True；历史栈为空返回 False（不崩溃）
        """
        if not self.history:
            return False
        last_state = self.history.pop()
        self.board = last_state["board"]
        self.current_player = last_state["current_player"]
        self.black_pieces = last_state["black_pieces"].copy()
        self.white_pieces = last_state["white_pieces"].copy()
        return True

    # ====================== 坐标工具 ======================
    def is_in_board(self, x: int, y: int) -> bool:
        """检查 (x, y) 是否在棋盘有效范围内。"""
        return 0 <= x < self.BOARD_SIZE and 0 <= y < self.BOARD_SIZE

    def get_piece_positions(self, player: int) -> list:
        """
        获取指定玩家的所有棋子坐标（返回副本，外部修改不影响内部）。
        :param player: BLACK / WHITE
        :return: [(x1,y1), (x2,y2), ...]
        """
        if player == self.BLACK:
            return self.black_pieces.copy()
        return self.white_pieces.copy()
