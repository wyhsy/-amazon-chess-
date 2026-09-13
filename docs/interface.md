# 接口契约（Interface Contract）

> **这是全队最重要的文档。** `ui.py`、`ai_search.py`、`ai_eval.py` 都建立在 `board.py` / `rule.py` 的公开接口之上。
> 任何人改动本文件描述的接口，都必须走第 6 节的变更流程。
>
> 状态：**草案 v0.1（待全队确认）**——第 1 节的 5 个决策点需要 4 位负责人在第 1 周内拍板，拍板后改为“已冻结 v1.0”。

---

## 1. 待拍板的决策点

| # | 决策点 | 推荐方案 | 理由 | 结论 |
| --- | --- | --- | --- | --- |
| D1 | 棋盘表示 | **一维 `list[int]`，长度 100，索引 `r * 10 + c`** | 拷贝/哈希极快（AI 搜索每步都要复制棋盘），比 10×10 嵌套 list 快得多 | 待定 |
| D2 | 坐标顺序 | **`(row, col)`，row=0 为最上面一行，col=0 为最左列** | 与打印输出、二维思维一致；渲染时 `x=col, y=row` | 待定 |
| D3 | 走法结构 | **`Move = namedtuple("Move", "src dst arrow")`**，三个元素都是 `(row, col)` | 可读、可解包、比自定义类轻；注意不要用 `from`（关键字）作字段名 | 待定 |
| D4 | 走法生成粒度 | **同时提供两种**：`legal_moves()` 一次性生成全部完整走法（UI/测试用）、`piece_targets()` + `shot_targets()` 分步生成（AI 搜索用，可按需剪枝） | UI 要方便，AI 要性能和剪枝空间 | 待定 |
| D5 | 棋盘可变性 | **`apply_move()` 返回新棋盘（不可变语义）**；AI 内部若性能不足，另用 `do_move()` / `undo_move()` 就地回溯 | 不可变语义最不容易写出 bug；回溯版是纯性能优化，接口分开以免污染语义 | 待定 |

**如果决策有分歧，以"AI 算法负责人 + 游戏规则负责人"的意见为准，其余人按结论执行，不在 PR 里重新争论。**

## 2. 棋盘数据模型（`board.py`）

```python
BOARD_SIZE = 10
CELL_COUNT = BOARD_SIZE * BOARD_SIZE   # 100

# 格子取值：只用这 4 个常量，禁止裸写 0/1/2/3
EMPTY = 0
BLACK = 1
WHITE = 2
ARROW = 3

Board = list[int]          # 长度 100，board[r * BOARD_SIZE + c]

def idx(r: int, c: int) -> int                  # (r, c) -> 一维下标
def rc(i: int) -> tuple[int, int]               # 一维下标 -> (r, c)
def at(board: Board, r: int, c: int) -> int     # 越界返回 None 还是报错？统一：返回 -1 表示越界
def clone(board: Board) -> Board                # 浅拷贝一维 list，O(100)
def initial_board() -> Board                    # 标准开局
def in_bounds(r: int, c: int) -> bool
```

**标准开局布局**（`(row, col)`，0 起）：

| 颜色 | 亚马逊所在格 |
| --- | --- |
| BLACK | `(0, 3)`、`(3, 0)`、`(6, 9)`、`(9, 6)` |
| WHITE | `(0, 6)`、`(3, 9)`、`(6, 0)`、`(9, 3)` |

> ⚠️ **落地前必须核对课程题目册/老师给的图示**（行 0 在顶还是底、黑白谁在哪个角）。
> 核对方式：把结论写成 `test/test_rule.py::test_initial_board` 里的断言，之后以测试为准，避免口头约定漂移。

## 3. 规则引擎（`rule.py`）

```python
WHITE_WIN = 1
BLACK_WIN = -1
DRAW = 0

def piece_targets(board: Board, r: int, c: int) -> list[tuple[int, int]]:
    """单个棋子的可移动目标格（皇后走法 + 马步），不包含射箭。"""

def shot_targets(board: Board, r: int, c: int) -> list[tuple[int, int]]:
    """从 (r, c) 射箭的可选落点（皇后走法 + 马步）。"""

def legal_moves(board: Board, color: int) -> list[Move]:
    """生成该方全部合法完整走法（移动 + 射箭）。开局量级为数千条，注意性能。"""

def is_legal(board: Board, move: Move, color: int) -> bool:
    """校验一条完整走法是否合法（供 UI 与测试使用）。"""

def apply_move(board: Board, move: Move, color: int) -> Board:
    """返回走完后的新棋盘，不修改入参 board。"""

def do_move(board: Board, move: Move, color: int) -> tuple:
    """就地执行走法，返回被覆盖格子的旧值（供 AI 回溯），仅 AI 搜索内部使用。"""

def undo_move(board: Board, move: Move, color: int, old: tuple) -> None:
    """与 do_move 配对，恢复棋盘。"""

def has_any_move(board: Board, color: int) -> bool:
    """该方是否还有棋可走（用于终局判定，应比 legal_moves 早退更高效）。"""

def territory(board: Board) -> tuple[int, int]:
    """(黑方可达格数, 白方可达格数)，用于终局计分与估值特征。"""

def game_result(board: Board) -> int | None:
    """None=未结束；DRAW=和棋；WHITE_WIN / BLACK_WIN=已分胜负。"""
```

**规则要点（实现时必须逐条写测试）**：

1. 一回合 = **先移动己方亚马逊，再从落点射箭**，两段都必须走皇后路线或马步，路径上不能有障碍（棋子或箭头）。
2. 射箭落点从落点出发计算，**箭不能射到自己所在格**。
3. 棋子和箭头占据的格子：不可通过、不可落子。
4. 该方 `has_any_move` 为 `False` 时该方判负；双方都无法走子为和棋。
5. 终局（或需要判断胜负时）用 `territory()` 比较领地——具体口径以题目册为准，写入测试固定。

## 4. 估值函数（`ai_eval.py`）

```python
DEFAULT_WEIGHTS: dict[str, float] = {...}

def evaluate(board: Board, color: int) -> int:
    """返回局面分数，正数表示对 color 有利，负数不利。"""

class Evaluator:
    def __init__(self, weights: dict[str, float] | None = None) -> None: ...
    def evaluate(self, board: Board, color: int) -> int: ...
```

**硬约束**：

- **零和一致性**：对任意棋盘，`evaluate(board, WHITE) == -evaluate(board, BLACK)`。写进测试。
- 建议特征集（可增减，但改动需与 AI 组同步）：机动性（双方可走格数之差）、领地差、棋子中心/边角权值、连通性与空间分割。
- 评估函数必须是纯函数，**不允许修改传入的 board**，也不允许 import pygame。

## 5. 搜索（`ai_search.py`）与界面（`ui.py`）

```python
# ai_search.py
def search(
    board: Board,
    color: int,
    depth: int = 2,
    time_limit: float | None = 3.0,
) -> Move | None:
    """返回该方最佳走法；无棋可走返回 None。超时返回当前已知最优。"""

# ui.py
class GameUI:
    def __init__(self, mode: str = "pve", human_color: int = WHITE,
                 difficulty: str = "normal") -> None: ...
    def run(self) -> None:
        """进入主循环，阻塞直到退出。"""

# main.py
def main() -> None:
    """解析命令行参数（--mode pvp|pve、--difficulty easy|normal|hard）并启动界面。"""
```

## 6. 依赖方向（单向，禁止反向 import）

```
        main.py
       /   |    \
    ui.py  |     ai_search.py
      \    |      /      \
       rule.py  ai_eval.py
           \      /
          board.py          ← 谁都不允许依赖 ui
```

| 模块 | 允许 import | 禁止 import |
| --- | --- | --- |
| `board.py` | 仅标准库 | 其它所有项目模块 |
| `rule.py` | `board` | `ui`、`ai_*` |
| `ai_eval.py` | `board` | `ui`、`rule`（可通过参数传入特征，不反向取） |
| `ai_search.py` | `board`、`rule`、`ai_eval` | `ui` |
| `ui.py` | `board`、`rule`、`ai_search` | `ai_eval`（估值细节属于 AI 组） |
| `main.py` | 全部 | — |

**禁止 `rule.py` / `board.py` / `ai_eval.py` / `ai_search.py` 中 import pygame**——保证这些模块能在无图形环境的 CI 里被测试。

## 7. 性能约定（Python 写棋类搜索的生死线）

- 棋盘复制一律用 `board[:]` 或 `list.copy()`，**禁止 `copy.deepcopy`**。
- AI 搜索优先使用 `do_move` / `undo_move` 就地回溯，避免每层复制。
- 单步思考时间上限默认 3 秒，通过 `time_limit` 控制，超时返回当前最优（不能卡住界面）。
- 建议在第 1 周先写一个性能基线脚本（临时文件，不入库）测量：`legal_moves()` 生成耗时、单层搜索节点数，用来决定是否需要置换表/走法排序优化。

## 8. 接口变更流程（红线②的具体操作）

1. 在 GitHub 开一个 Issue，标题以 `[interface]` 开头，说明改什么、为什么。
2. 群内 @ 全部 3 位队友（尤其受影响的模块负责人）。
3. 修改代码 + **同一 PR 内更新本文件**（版本号 +1，附变更说明）。
4. 排查并同步所有调用点：`grep -rn "被改的函数名" .`
5. PR 必须由受影响模块的负责人 Review 通过后才能合并。

## 9. 变更记录

| 版本 | 日期 | 改动 | 作者 |
| --- | --- | --- | --- |
| v0.1 | 待填 | 初稿：确定模块边界与签名草案 | — |
