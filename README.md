# -amazon-chess-

亚马逊棋人机博弈课程设计项目 | 肆如破竹小组

## 项目简介

基于 Python + Pygame 开发的亚马逊棋（Amazon Chess）人机对战游戏，实现完整棋规、Minimax 博弈算法、Alpha-Beta 剪枝优化，支持人人对战与人机对战模式。

## 技术栈

- 编程语言：Python 3.9+
- 图形界面：Pygame
- 核心算法：Minimax + Alpha-Beta 剪枝
- 测试框架：pytest
- 版本控制：Git + GitHub（CI 自动跑测试）

## 快速开始

```bash
# 1. 克隆仓库并进入目录（仓库名首尾带连字符，需加引号）
git clone https://github.com/wyhsy/-amazon-chess-.git
cd "-amazon-chess-"

# 2. 切到开发分支
git checkout -b dev origin/dev

# 3. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
# source .venv/bin/activate       # macOS / Linux

# 4. 安装依赖
pip install -r requirements-dev.txt

# 5. 运行游戏
python main.py

# 6. 运行测试
pytest -q
```

## 目录结构

```
-amazon-chess-/
├── main.py              # 程序入口（组装棋盘、规则、界面、AI）
├── board.py             # 棋盘数据模型（棋盘表示、初始化、坐标工具）
├── rule.py              # 规则引擎、走法生成、胜负判定
├── ui.py                # Pygame 界面交互、渲染、动画
├── ai_search.py         # Minimax 搜索、Alpha-Beta 剪枝
├── ai_eval.py           # 局面估值函数、权重配置
├── assets/              # 图片、音效等素材
├── test/                # 单元测试（pytest，命名 test_*.py）
│   ├── test_smoke.py    # 环境冒烟测试（M1 后可删除）
│   ├── test_rule.py
│   ├── test_search.py
│   └── test_eval.py
├── docs/                # 项目文档
│   ├── plan.md          # 分工、里程碑、协作节奏
│   ├── interface.md     # 接口契约（改动前必读）
│   ├── setup.md         # 环境搭建与常用 Git 操作
│   └── meeting/         # 会议记录
├── .github/             # PR/Issue 模板、CODEOWNERS、CI
├── requirements.txt     # 运行期依赖
└── requirements-dev.txt # 开发/测试依赖
```

> 代码文件按上表划分归属，**只改自己负责的模块**；接口调整流程见 `CONTRIBUTING.md`。

## 团队分工

| 角色 | 负责人 | 负责文件 | 主要工作 |
| --- | --- | --- | --- |
| 界面设计 | @guoyi1005 | `ui.py`、`assets/` | 棋盘与棋子渲染、选中/落子交互、走法提示、胜负提示与动画 |
| 游戏规则 | @xiong681 | `board.py`、`rule.py`、`test/test_rule.py` | 棋盘数据模型、8 方向走法生成、炮台遮挡判定、终局与计分 |
| AI 算法 | @wyhsy | `ai_search.py`、`test/test_search.py` | Minimax 框架、Alpha-Beta 剪枝、迭代加深/时限控制、性能优化 |
| 评估策略 | @qiqiyuexi | `ai_eval.py`、`test/test_eval.py`、`docs/` | 估值函数设计、权重调优、实验对比、报告与答辩材料 |

（详细职责边界与依赖关系见 `docs/plan.md`；模块归属记录在 `.github/CODEOWNERS`）

> **本项目的 GitHub 操作由组长 @wyhsy 统一负责**（定接口、派任务、审阅合并 PR、发布 main）；队友只需完成自己模块的文件并提 PR。

## 玩法与规则要点

亚马逊棋：10×10 棋盘，黑白各 4 个"亚马逊"（同时具备国际象棋中皇后 + 马的走法）。

- 一回合内，当前方需要**依次**完成两件事：
  1. 移动一个己方亚马逊（走皇后路线或马步，路径需无障碍）
  2. 该亚马逊从落点**射出一支箭**（同样走皇后路线或马步，路径需无障碍），箭头落点变为永久障碍
- 已被占据（棋子或箭头）的格子不可通过、不可落子
- **无法走子的一方判负**；若双方都无法走子则为和棋
- 常见补充判定：终局时比较各自可活动的格子数（领地）决定胜负

> 规则的细节以课程题目册与 `docs/` 内说明为准；实现上以 `rule.py` 的测试用例为准。

## AI 设计概要

- **搜索**：Minimax + Alpha-Beta 剪枝；按"移动 + 射箭"拆分搜索层，配合走法排序提升剪枝效率
- **评估**：综合机动性（可走格数）、领地控制、棋子位置权值、连通性等特征加权求和
- **性能**：单步思考时间上限可配置（默认 ≤ 3 秒），超时返回当前最优走法；后续可加置换表、迭代加深
- **难度**：至少提供"简单 / 普通 / 困难"三档，对应不同搜索深度或时间上限

## 开发进度

- [x] 仓库创建、协作规范（README / CONTRIBUTING / CI / 分支保护）
- [x] 接口契约冻结（`docs/interface.md` v1.0，2026-09-13）
- [ ] **M1 规则地基**：`board.py` + `rule.py` + 单元测试全绿
- [ ] **M2 可玩**：`ui.py` 人人对战可下完完整一局
- [ ] **M3 AI 接入**：Minimax + Alpha-Beta 人机对战
- [ ] **M4 打磨**：估值调优、难度分级、性能优化、报告与答辩材料

里程碑验收标准见 `docs/plan.md`。

## 文档索引

| 文档 | 用途 |
| --- | --- |
| `CONTRIBUTING.md` | 协作流程、分支与提交规范、红线（**新成员必读**） |
| `docs/plan.md` | 分工、里程碑、每周节奏、风险清单 |
| `docs/interface.md` | 接口契约：棋盘表示、Move 结构、模块函数签名 |
| `docs/setup.md` | 环境搭建、常用 Git 操作步骤 |
| `docs/tasks/` | **任务派发书**（每个模块交什么、怎么验收，队友看这里） |

## 环境要求

- Python 3.9 或更高（CI 覆盖 3.9 / 3.11）
- 操作系统：Windows / macOS / Linux 均可
- 依赖：见 `requirements.txt`、`requirements-dev.txt`
