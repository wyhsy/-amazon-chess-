"""
test_rule.py - 规则引擎单元测试
运行方式：在 amazon-chess/ 目录下执行  pytest test/test_rule.py -v
（未安装 pytest 时也可直接运行，内置兼容替代）
覆盖：初始化一致性、走法生成、合法性校验、箭射回原位置、
      缓存同步、撤销恢复、完整对局、边界健壮性、终局判定。
"""
import sys
import os
import random

# 让 test/ 目录能导入上级目录的 board.py / rule.py
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# pytest 兼容：未安装时用简易替代，保证测试可直接运行
try:
    import pytest
    _raises = pytest.raises
except ImportError:
    class _raises:
        """简易 pytest.raises 替代，仅支持异常类型校验。"""
        def __init__(self, exc_type):
            self.exc_type = exc_type
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"期望抛出 {self.exc_type.__name__}，但未抛出")
            return issubclass(exc_type, self.exc_type)

from board import AmazonsBoard
from rule import AmazonsRule


# ====================== 辅助函数 ======================
def check_cache_consistency(b: AmazonsBoard):
    """校验棋子缓存与棋盘数组完全一致。"""
    for (x, y) in b.black_pieces:
        assert b.board[y][x] == b.BLACK, f"黑棋缓存({x},{y})与棋盘不一致"
    for (x, y) in b.white_pieces:
        assert b.board[y][x] == b.WHITE, f"白棋缓存({x},{y})与棋盘不一致"
    bp = set(b.black_pieces)
    wp = set(b.white_pieces)
    for y in range(10):
        for x in range(10):
            v = b.board[y][x]
            if v == b.BLACK:
                assert (x, y) in bp, f"棋盘黑棋({x},{y})不在缓存中"
            if v == b.WHITE:
                assert (x, y) in wp, f"棋盘白棋({x},{y})不在缓存中"


def make_board():
    """创建并初始化标准棋盘。"""
    b = AmazonsBoard()
    b.init_standard()
    return b


# ====================== 1. 初始化与数据模型 ======================
class TestInit:
    def test_standard_opening_piece_count(self):
        b = make_board()
        assert len(b.black_pieces) == 4
        assert len(b.white_pieces) == 4

    def test_standard_opening_positions(self):
        b = make_board()
        assert set(b.black_pieces) == {(0, 6), (9, 6), (3, 9), (6, 9)}
        assert set(b.white_pieces) == {(3, 0), (6, 0), (0, 3), (9, 3)}

    def test_board_matches_cache(self):
        b = make_board()
        check_cache_consistency(b)

    def test_first_player_is_black(self):
        b = make_board()
        assert b.current_player == AmazonsBoard.BLACK

    def test_history_empty_after_init(self):
        b = make_board()
        assert len(b.history) == 0


# ====================== 2. 坐标工具 ======================
class TestIsInBoard:
    def test_inside(self):
        b = make_board()
        assert b.is_in_board(0, 0) is True
        assert b.is_in_board(9, 9) is True
        assert b.is_in_board(5, 5) is True

    def test_outside(self):
        b = make_board()
        assert b.is_in_board(-1, 0) is False
        assert b.is_in_board(0, -1) is False
        assert b.is_in_board(10, 0) is False
        assert b.is_in_board(0, 10) is False


# ====================== 3. 走法生成 ======================
class TestGenerateMoves:
    def test_first_move_count(self):
        """标准开局黑方首步合法走法数应为 2176。"""
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        assert len(moves) == 2176

    def test_move_dict_keys(self):
        """每个走法字典必须包含 6 个标准 key。"""
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        required = {"from_x", "from_y", "to_x", "to_y", "arrow_x", "arrow_y"}
        for m in moves[:50]:
            assert required.issubset(m.keys())

    def test_generated_moves_are_applicable(self):
        """生成的走法必须全部能通过 apply_move（不抛异常）。"""
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        random.seed(42)
        for m in random.sample(moves, 300):
            c = b.clone()
            AmazonsRule.apply_move(c, m)
            check_cache_consistency(c)

    def test_arrow_back_to_origin_exists(self):
        """箭射回原位置的走法应存在（开局 80 种）。"""
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        back = [m for m in moves
                if m["arrow_x"] == m["from_x"] and m["arrow_y"] == m["from_y"]]
        assert len(back) == 80


# ====================== 4. 合法性校验 ======================
class TestValidation:
    def test_valid_move(self):
        b = make_board()
        # 黑棋 (0,6) 向右移动到 (1,6)，路径通畅
        assert AmazonsRule.is_valid_move(b, 0, 6, 1, 6) is True

    def test_invalid_move_wrong_piece(self):
        b = make_board()
        # 当前是黑方，移动白棋不合法
        assert AmazonsRule.is_valid_move(b, 3, 0, 3, 1) is False

    def test_invalid_move_blocked(self):
        b = make_board()
        # 黑棋 (0,6) 向上到 (0,0)，路径上 (0,3) 是白棋 → 路径被阻挡
        assert AmazonsRule.is_valid_move(b, 0, 6, 0, 0) is False

    def test_invalid_move_non_straight(self):
        b = make_board()
        # 非直线移动（马走日，横纵距离不等）
        assert AmazonsRule.is_valid_move(b, 0, 6, 1, 8) is False

    def test_arrow_start_out_of_bounds(self):
        """射箭起点越界应返回 False，不崩溃。"""
        b = make_board()
        assert AmazonsRule.is_valid_arrow(b, 15, 15, 3, 3) is False

    def test_arrow_start_not_piece(self):
        """射箭起点不是己方棋子应返回 False。"""
        b = make_board()
        assert AmazonsRule.is_valid_arrow(b, 5, 5, 3, 3) is False

    def test_arrow_same_as_start(self):
        """原地射箭不合法。"""
        b = make_board()
        # 临时把 (5,5) 变成黑棋来测试
        b.board[5][5] = b.BLACK
        assert AmazonsRule.is_valid_arrow(b, 5, 5, 5, 5) is False


# ====================== 5. 执行走法与缓存同步 ======================
class TestApplyMove:
    def test_apply_switches_player(self):
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        AmazonsRule.apply_move(b, moves[0])
        assert b.current_player == AmazonsBoard.WHITE

    def test_apply_updates_cache(self):
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        AmazonsRule.apply_move(b, moves[0])
        check_cache_consistency(b)

    def test_arrow_back_to_origin(self):
        """箭射回原位置：原格应变为障碍，棋子到新位置。"""
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        back = [m for m in moves
                if m["arrow_x"] == m["from_x"] and m["arrow_y"] == m["from_y"]]
        m = back[0]
        AmazonsRule.apply_move(b, m)
        assert b.board[m["from_y"]][m["from_x"]] == b.OBSTACLE
        assert b.board[m["to_y"]][m["to_x"]] == b.BLACK  # 上一步是黑方走的，棋子是黑棋
        check_cache_consistency(b)

    def test_invalid_move_raises_and_no_pollution(self):
        """非法走法抛异常，且历史栈和棋盘状态不被污染。"""
        b = make_board()
        with _raises(ValueError):
            AmazonsRule.apply_move(b, {
                "from_x": 0, "from_y": 3,  # 白棋位置，当前是黑方
                "to_x": 1, "to_y": 3,
                "arrow_x": 0, "arrow_y": 0
            })
        assert len(b.history) == 0
        check_cache_consistency(b)

    def test_cache_mismatch_raises(self):
        """缓存与棋盘不一致时拒绝执行，不污染状态。"""
        b = make_board()
        b.board[0][3] = b.EMPTY  # 直接改棋盘，缓存失配
        with _raises(ValueError):
            AmazonsRule.apply_move(b, {
                "from_x": 0, "from_y": 3,
                "to_x": 2, "to_y": 3,
                "arrow_x": 0, "arrow_y": 0
            })
        assert len(b.history) == 0


# ====================== 6. 撤销 ======================
class TestUndo:
    def test_undo_restores_state(self):
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        AmazonsRule.apply_move(b, moves[0])
        assert AmazonsRule.undo_move(b) is True
        check_cache_consistency(b)
        assert b.current_player == b.BLACK
        assert len(b.history) == 0

    def test_undo_empty_history(self):
        b = make_board()
        assert AmazonsRule.undo_move(b) is False

    def test_restore_state_empty(self):
        b = make_board()
        assert b.restore_state() is False

    def test_multiple_undo(self):
        b = make_board()
        random.seed(42)
        for _ in range(15):
            ms = AmazonsRule.generate_all_legal_moves(b)
            if not ms:
                break
            AmazonsRule.apply_move(b, random.choice(ms))
        for _ in range(15):
            if not AmazonsRule.undo_move(b):
                break
            check_cache_consistency(b)


# ====================== 7. 克隆 ======================
class TestClone:
    def test_clone_independent(self):
        b = make_board()
        c = b.clone()
        moves = AmazonsRule.generate_all_legal_moves(c)
        AmazonsRule.apply_move(c, moves[0])
        # 原棋盘不受影响
        check_cache_consistency(b)
        check_cache_consistency(c)
        assert b.current_player == b.BLACK
        assert c.current_player == c.WHITE

    def test_clone_does_not_copy_history(self):
        b = make_board()
        moves = AmazonsRule.generate_all_legal_moves(b)
        AmazonsRule.apply_move(b, moves[0])
        c = b.clone()
        assert len(c.history) == 0


# ====================== 8. 终局判定 ======================
class TestGameOver:
    def test_not_over_at_start(self):
        b = make_board()
        assert AmazonsRule.check_game_over(b) is None

    def test_has_no_legal_moves_false_at_start(self):
        b = make_board()
        assert AmazonsRule.has_no_legal_moves(b, b.BLACK) is False
        assert AmazonsRule.has_no_legal_moves(b, b.WHITE) is False

    def test_full_random_game_terminates(self):
        """随机对局最多 200 步内必然终局（亚马逊棋有限局）。"""
        b = make_board()
        random.seed(42)
        for _ in range(200):
            ms = AmazonsRule.generate_all_legal_moves(b)
            if not ms:
                break
            AmazonsRule.apply_move(b, random.choice(ms))
            check_cache_consistency(b)
            result = AmazonsRule.check_game_over(b)
            if result:
                assert "winner" in result
                assert "loser" in result
                return
        # 如果 200 步没终局，检查是否真的无棋可走
        assert AmazonsRule.has_no_legal_moves(b, b.current_player)


# ====================== 9. 对外工具接口 ======================
class TestGetPiecePositions:
    def test_returns_copy(self):
        b = make_board()
        pos = b.get_piece_positions(b.BLACK)
        pos.append((99, 99))
        assert (99, 99) not in b.black_pieces

    def test_returns_correct_positions(self):
        b = make_board()
        assert set(b.get_piece_positions(b.BLACK)) == {(0, 6), (9, 6), (3, 9), (6, 9)}
        assert set(b.get_piece_positions(b.WHITE)) == {(3, 0), (6, 0), (0, 3), (9, 3)}
