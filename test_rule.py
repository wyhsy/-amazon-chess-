"""
test_rule.py - 规则引擎单元测试（接口契约 v1.0）
运行方式：pytest test/test_rule.py -v
覆盖：board 工具函数、走法生成、合法性校验、不可变 apply、就地回溯、终局判定、领地计算。
"""
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import pytest
    _raises = pytest.raises
except ImportError:
    class _raises:
        def __init__(self, exc_type):
            self.exc_type = exc_type
        def __enter__(self):
            return self
        def __exit__(self, exc_type, exc_val, exc_tb):
            if exc_type is None:
                raise AssertionError(f"期望抛出 {self.exc_type.__name__}，但未抛出")
            return issubclass(exc_type, self.exc_type)

from board import (
    BOARD_SIZE, CELL_COUNT, EMPTY, BLACK, WHITE, ARROW,
    idx, rc, in_bounds, at, clone, initial_board, empty_board, count, to_text,
)
from rule import (
    WHITE_WIN, BLACK_WIN, DRAW, Move,
    piece_targets, shot_targets, legal_moves, is_legal,
    apply_move, do_move, undo_move, has_any_move, territory, game_result,
)


# ====================== board.py 测试 ======================
class TestBoard:
    def test_idx_rc_roundtrip(self):
        for r in range(BOARD_SIZE):
            for c in range(BOARD_SIZE):
                i = idx(r, c)
                assert rc(i) == (r, c)
                assert 0 <= i < CELL_COUNT

    def test_in_bounds(self):
        assert in_bounds(0, 0) is True
        assert in_bounds(9, 9) is True
        assert in_bounds(-1, 0) is False
        assert in_bounds(0, 10) is False
        assert in_bounds(10, 10) is False

    def test_at_out_of_bounds_returns_minus1(self):
        b = initial_board()
        assert at(b, -1, 0) == -1
        assert at(b, 0, 10) == -1

    def test_clone_is_independent(self):
        b = initial_board()
        c = clone(b)
        c[0] = ARROW
        assert b[0] != c[0]

    def test_initial_board_piece_count(self):
        b = initial_board()
        assert count(b, BLACK) == 4
        assert count(b, WHITE) == 4
        assert count(b, ARROW) == 0
        assert count(b, EMPTY) == 92

    def test_initial_board_positions(self):
        b = initial_board()
        for r, c in [(0, 3), (3, 0), (6, 9), (9, 6)]:
            assert at(b, r, c) == BLACK
        for r, c in [(0, 6), (3, 9), (6, 0), (9, 3)]:
            assert at(b, r, c) == WHITE

    def test_empty_board(self):
        b = empty_board()
        assert count(b, EMPTY) == CELL_COUNT
        assert len(b) == CELL_COUNT

    def test_to_text_returns_string(self):
        b = initial_board()
        text = to_text(b)
        assert isinstance(text, str)
        assert 'B' in text
        assert 'W' in text


# ====================== 走法生成测试 ======================
class TestMoveGeneration:
    def test_piece_targets_for_black_piece(self):
        b = initial_board()
        # BLACK at (0,3)，能向右、向下、右下等方向移动
        targets = piece_targets(b, 0, 3)
        assert len(targets) > 0
        assert (0, 4) in targets  # 向右
        assert (1, 3) in targets  # 向下

    def test_piece_targets_empty_cell(self):
        b = initial_board()
        assert piece_targets(b, 5, 5) == []

    def test_shot_targets_same_as_piece_targets(self):
        b = initial_board()
        # 从棋子位置出发，两者规则完全相同（都是皇后8方向直线）
        assert shot_targets(b, 0, 3) == piece_targets(b, 0, 3)

    def test_legal_moves_returns_move_objects(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        assert len(moves) > 0
        for m in moves[:20]:
            assert isinstance(m, Move)
            assert hasattr(m, 'src')
            assert hasattr(m, 'dst')
            assert hasattr(m, 'arrow')

    def test_legal_moves_does_not_mutate_board(self):
        b = initial_board()
        snapshot = b[:]
        legal_moves(b, BLACK)
        assert b == snapshot

    def test_legal_moves_both_colors_nonempty(self):
        b = initial_board()
        assert len(legal_moves(b, BLACK)) > 0
        assert len(legal_moves(b, WHITE)) > 0


# ====================== 合法性校验测试 ======================
class TestIsLegal:
    def test_legal_move_from_generated(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        assert is_legal(b, m, BLACK) is True

    def test_illegal_wrong_color(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        assert is_legal(b, m, WHITE) is False

    def test_illegal_dst_occupied(self):
        b = initial_board()
        # BLACK at (0,3) 试图移到 WHITE at (0,6)
        m = Move(src=(0, 3), dst=(0, 6), arrow=(0, 4))
        assert is_legal(b, m, BLACK) is False

    def test_illegal_non_straight(self):
        b = initial_board()
        # 马走日，非直线
        m = Move(src=(0, 3), dst=(1, 5), arrow=(0, 4))
        assert is_legal(b, m, BLACK) is False


# ====================== apply_move（不可变）测试 ======================
class TestApplyMove:
    def test_returns_new_board(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        new_b = apply_move(b, m, BLACK)
        assert new_b is not b
        assert b == initial_board()  # 原棋盘未被修改

    def test_piece_moved_and_arrow_placed(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        new_b = apply_move(b, m, BLACK)
        assert at(new_b, m.src[0], m.src[1]) == EMPTY
        assert at(new_b, m.dst[0], m.dst[1]) == BLACK
        assert at(new_b, m.arrow[0], m.arrow[1]) == ARROW

    def test_all_generated_moves_applicable(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        random.seed(42)
        for m in random.sample(moves, min(100, len(moves))):
            new_b = apply_move(b, m, BLACK)
            assert at(new_b, m.dst[0], m.dst[1]) == BLACK
            assert at(new_b, m.arrow[0], m.arrow[1]) == ARROW


# ====================== do_move / undo_move（就地回溯）测试 ======================
class TestDoUndoMove:
    def test_do_undo_restores_board(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        snapshot = b[:]
        old = do_move(b, m, BLACK)
        assert b != snapshot  # 已修改
        undo_move(b, m, BLACK, old)
        assert b == snapshot  # 已恢复

    def test_do_move_returns_three_old_values(self):
        b = initial_board()
        moves = legal_moves(b, BLACK)
        m = moves[0]
        old = do_move(b, m, BLACK)
        assert len(old) == 3
        undo_move(b, m, BLACK, old)

    def test_multiple_do_undo(self):
        b = initial_board()
        random.seed(42)
        snapshots = []
        for _ in range(10):
            moves = legal_moves(b, BLACK)
            if not moves:
                break
            m = random.choice(moves)
            snapshots.append((b[:], m, do_move(b, m, BLACK)))
            # 切换颜色模拟对局（简化：交替用 BLACK/WHITE 的合法走法）
        for snap_b, m, old in reversed(snapshots):
            undo_move(b, m, BLACK, old)
            assert b == snap_b


# ====================== 终局判定测试 ======================
class TestGameOver:
    def test_not_over_at_start(self):
        b = initial_board()
        assert game_result(b) is None

    def test_has_any_move_true_at_start(self):
        b = initial_board()
        assert has_any_move(b, BLACK) is True
        assert has_any_move(b, WHITE) is True

    def test_has_any_move_false_when_trapped(self):
        # 构造一个被完全困住的棋子
        b = empty_board()
        b[idx(0, 0)] = BLACK
        # 用箭把 (0,0) 周围全封死
        for r, c in [(0, 1), (1, 0), (1, 1)]:
            b[idx(r, c)] = ARROW
        assert has_any_move(b, BLACK) is False

    def test_game_result_white_win_when_black_trapped(self):
        b = empty_board()
        b[idx(0, 0)] = BLACK
        b[idx(9, 9)] = WHITE
        for r, c in [(0, 1), (1, 0), (1, 1)]:
            b[idx(r, c)] = ARROW
        # BLACK 被困，WHITE 还能走
        assert game_result(b) == WHITE_WIN

    def test_game_result_draw_when_both_trapped(self):
        b = empty_board()
        b[idx(0, 0)] = BLACK
        b[idx(9, 9)] = WHITE
        for r, c in [(0, 1), (1, 0), (1, 1)]:
            b[idx(r, c)] = ARROW
        for r, c in [(9, 8), (8, 9), (8, 8)]:
            b[idx(r, c)] = ARROW
        assert game_result(b) == DRAW

    def test_random_game_terminates(self):
        b = initial_board()
        random.seed(42)
        color = BLACK
        for _ in range(300):
            moves = legal_moves(b, color)
            if not moves:
                break
            m = random.choice(moves)
            b = apply_move(b, m, color)
            color = WHITE if color == BLACK else BLACK
        result = game_result(b)
        assert result in (WHITE_WIN, BLACK_WIN, DRAW)


# ====================== 领地计算测试 ======================
class TestTerritory:
    def test_territory_returns_pair(self):
        b = initial_board()
        bt, wt = territory(b)
        assert isinstance(bt, int)
        assert isinstance(wt, int)
        assert bt >= 0
        assert wt >= 0

    def test_territory_empty_board_zero(self):
        b = empty_board()
        assert territory(b) == (0, 0)

    def test_territory_single_piece(self):
        b = empty_board()
        b[idx(4, 4)] = BLACK
        bt, _ = territory(b)
        # (4,4) 周围8格都是空，所以黑方领地=8
        assert bt == 8
