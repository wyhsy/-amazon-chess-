# 贡献指南（CONTRIBUTING）

本文档规定 `-amazon-chess-` 项目的团队协作开发流程，所有参与开发的成员请严格遵循本规范。
第 3 节是最常用的日常流程；新成员请先完整读第 1、2 节。

---

## 0. 角色与模块归属

| 模块 | 负责人 | 主要文件 | 说明 |
| --- | --- | --- | --- |
| 界面设计 | @guoyi1005 | `ui.py`、`assets/` | Pygame 渲染、交互、动画、提示 |
| 游戏规则 | @xiong681 | `board.py`、`rule.py`、`test/test_rule.py` | 棋盘数据模型、走法生成、胜负判定（**地基模块**） |
| AI 算法 | @wyhsy | `ai_search.py`、`test/test_search.py`、`main.py` | Minimax、Alpha-Beta 剪枝、迭代加深、置换表 |
| 评估策略 | @qiqiyuexi | `ai_eval.py`、`test/test_eval.py`、`docs/` | 局面估值函数、权重调优、报告与答辩材料 |

> `CODEOWNERS` 里记录了每个模块的负责人（`@wyhsy`=AI 算法、`@guoyi1005`=界面、`@xiong681`=规则、`@qiqiyuexi`=评估），作用是**标明文件归属**，不是要求谁来批准。
>
> **本项目的 GitHub 操作由组长（@wyhsy）统一负责**：
>
> | 角色 | 负责的事 |
> | --- | --- |
> | 组长 @wyhsy | 定接口与里程碑（见 `docs/interface.md`）、派发任务、审阅并合并所有 PR、`main` 发布、维护 `.github/` 与 CI |
> | 队友 @guoyi1005 / @xiong681 / @qiqiyuexi | 按派发任务实现自己模块的文件 → 本地跑通 `pytest -q` → 开 feature 分支提 PR（**不需要 Approve 任何 PR，也不需要碰仓库设置**） |
>
> **只改自己模块的文件**；需要改接口或动别人文件，先在群里说明，由组长拍板。

## 1. 前置准备

### 1.1 接受仓库邀请

1. 登录 GitHub，点击右上角通知铃铛
2. 找到 `-amazon-chess-` 仓库的协作者邀请，点击 **Accept invitation**
3. 接受后获得 Write 权限，可推送代码、发起 PR

### 1.2 本地仓库初始化（仅首次）

```bash
# 克隆（仓库名首尾带连字符，命令里请加引号）
git clone https://github.com/wyhsy/-amazon-chess-.git
cd "-amazon-chess-"

# 创建并切换到本地 dev 分支（跟踪远程 dev）
git checkout -b dev origin/dev

# 建虚拟环境（不要用全局 Python，避免“我这能跑你那不能跑”）
python -m venv .venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS / Linux:
source .venv/bin/activate

# 安装依赖
pip install -r requirements-dev.txt
```

`git branch` 输出同时包含 `main` 和 `dev` 即配置完成。
验证环境可用：`pytest -q`（应显示测试结果，不报 `ModuleNotFoundError`）。

### 1.3 必须知道的仓库设置

- 仓库默认分支是 `main`，但**日常开发都在 `dev` 上进行**，不要基于 main 开工。
- `main` / `dev` 已开启分支保护：**不允许直接 push，必须通过 PR**。本地被拒绝是正常现象，不是你的账号有问题。
- CI（`.github/workflows/ci.yml`）会在 PR 上自动跑 `pytest`，**CI 未通过不能合并**。
- PR **不需要任何人批准**，但必须等 CI 变绿；**合并由组长执行**，你只要把 PR 提出来、在群里说一声即可。

## 2. 分支管理规范

| 分支类型 | 分支名 | 作用 | 操作权限 |
| --- | --- | --- | --- |
| 主分支 | `main` | 稳定可运行版本，用于里程碑发布、答辩演示 | 禁止直接提交，仅从 `dev` 合并 |
| 开发分支 | `dev` | 团队集成分支，所有功能最终汇合于此 | 禁止直接推送，只能通过 PR 合并 |
| 功能分支 | `feature/<英文模块名>` | 单个功能的临时分支，合并后删除 | 开发者自行创建、提交、推送 |
| 修复分支 | `hotfix/<问题名>` | 已合并代码上的紧急修复 | 同上，目标分支为 `dev` |

### 分支命名（统一用英文，避免 Windows 中文路径编码问题）

| 场景 | 分支名示例 |
| --- | --- |
| 规则引擎 | `feature/rule-engine` |
| 走法生成 | `feature/legal-moves` |
| 界面 | `feature/ui-pygame` |
| 界面动画 | `feature/ui-animation` |
| AI 搜索 | `feature/ai-search` |
| 剪枝优化 | `feature/alpha-beta` |
| 估值函数 | `feature/eval-weights` |
| 文档/报告 | `docs/report-outline` |

**命名要求**：全小写英文 + 连字符；不要用中文、不要用空格、不要用 `feature/张三的活` 这类无信息量名称。

**粒度要求**：一个分支只做一件事。开发到一半发现另一个 bug，不要顺手一起改，另开分支。

## 3. 日常开发工作流

### 步骤 1：同步最新代码（每次开工前必做）

```bash
git checkout dev
git pull origin dev
```

### 步骤 2：创建功能分支

```bash
git checkout -b feature/模块名
```

### 步骤 3：本地开发与自测（提交前的门槛）

```bash
pytest -q            # 全绿再提交
python main.py       # 至少跑一遍涉及到的路径
```

### 步骤 4：提交并推送

```bash
git add .
git status           # 确认没有 __pycache__、.venv、本地截图混进来
git commit -m "feat(rule): 生成全部合法走法"
git push origin feature/模块名
```

### 步骤 5：发起 Pull Request

1. 打开仓库页面，顶部会出现「Compare & pull request」
2. 源分支 = 你的功能分支，目标分支 = **`dev`**（不要选 main）
3. 按 `.github/pull_request_template.md` 模板填写：改了什么、怎么测的、是否影响接口
4. 关联对应 Issue（PR 描述里写 `Closes #12`）
5. 等待 CI 变绿（4 个 `pytest` 全 ✅），然后在群里 @ 组长来合并

### 步骤 6：合并与清理（合并由组长做）

- 组长用 **Squash and merge** 合并（一个功能 = 一条 dev 提交记录，历史干净），并删掉远程功能分支
- 你在本地清理：

```bash
git checkout dev
git pull origin dev
git branch -d feature/模块名
```

### 步骤 7：里程碑发布（只有组长执行）

`dev` 验收通过后，由组长发起 `dev → main` 的 PR，合并并打 tag（如 `v1.0`）。

## 4. 提交信息规范

统一采用 **Conventional Commits**：`类型(模块): 描述`，描述用中文、动词开头、不加句号。

| 类型 | 说明 |
| --- | --- |
| `feat` | 新增功能 |
| `fix` | 修复 Bug |
| `docs` | 文档、README |
| `refactor` | 重构，不改变外部行为 |
| `test` | 测试代码 |
| `style` | 格式调整（空格、换行），不影响运行 |
| `perf` | 性能优化（AI 搜索加速常用） |
| `chore` | 杂项（依赖、配置、CI） |

**模块 scope**（强烈建议填写，便于按模块筛选历史）：
`rule` / `board` / `ui` / `ai-search` / `ai-eval` / `docs` / `ci`

```bash
feat(rule): 生成全部合法走法
fix(rule): 修复终局判定把和棋误判为胜局
fix(ui): 修复选中棋子后点击非法格崩溃
perf(ai-search): 用一维数组替代 deepcopy，单步提速约 3 倍
test(rule): 补充炮台遮挡的边界用例
docs(readme): 补充环境搭建与分工说明
```

**禁止**：

- 只写「更新」「修改」「改了一下」这类无信息量的描述
- 一次性提交几十个文件却说不清改了什么
- 提交 `__pycache__/`、`.venv/`、IDE 配置、本地调试截图、临时日志

## 5. 代码冲突处理

```bash
git checkout dev
git pull origin dev

git checkout feature/模块名
git rebase dev           # 推荐 rebase，历史更线性、避免多余的合并提交
# 若出现冲突：编辑冲突文件 → git add <文件> → git rebase --continue
# 想放弃本次 rebase：git rebase --abort
```

rebase 后需要强推自己的功能分支（**仅限自己的功能分支**）：

```bash
git push --force-with-lease origin feature/模块名
```

> 绝对不要对 `main` / `dev` 使用 `--force` 或 `--force-with-lease`。

冲突解决原则：**自己模块内的事自己定，跨模块的事找组长裁定**。若冲突出现在别人负责的文件里，不要自行决定实现方式，先在群里说明，由组长决定怎么合。接口相关的冲突由组长处理（`docs/interface.md` 是唯一口径）。

## 6. 协作红线（必须遵守）

1. **禁止直接向 `main` / `dev` 推送代码**，所有改动必须通过 PR 合并
   （已由 GitHub 分支保护强制，不是靠自觉）
2. **只修改自己负责模块的文件**。确实需要改动他人文件时，必须先开 Issue 说明、@ 对方在本 PR 中确认；接口类改动还需同步更新 `docs/interface.md`
3. **接口由组长统一维护**：`board.py` / `rule.py` 的公开函数签名以 `docs/interface.md` **v1.0** 为准；确需改动时先在群里说明，由组长确认并同步所有调用点，不要自行改签名
4. 一个功能分支只做一件事，不混合无关改动
5. 提交信息遵循第 4 节规范，禁止模糊描述
6. 提交前必须 `pytest -q` 通过；冲突必须在本地解决完成后再提 PR
7. 不要提交虚拟环境、缓存目录、本地截图、日志文件

## 7. 常见问题

- **`git push` 被拒绝（protected branch）**：正常，说明分支保护生效了。请按第 3 节改走 PR 流程。
- **连接失败 / Connection reset / 拉取超时**：GitHub 国内网络不稳定。
  推荐做法（按优先级）：
  1. 配置 Git 走本地代理（已装 Clash/V2Ray 的同学）：
     ```bash
     git config --global http.proxy http://127.0.0.1:7890
     git config --global https.proxy http://127.0.0.1:7890
     # 取消：git config --global --unset http.proxy
     ```
  2. 使用 SSH 方式推送（配好 key 后比 HTTPS 稳定）
  3. 多次重试 / 换时间段

  > ⚠️ **不要**给同一份代码配 Gitee + GitHub 双远端做"镜像同步"，新手极易同步错方向或把代码推到错误仓库，造成版本混乱。
- **分支已存在报错**：本地已有同名分支时，直接 `git checkout 分支名` 切换即可。
- **`ModuleNotFoundError: No module named 'pygame'`**：没有激活虚拟环境或没装依赖，回到 1.2 节。
- **`pytest` 找不到测试**：确认测试文件在 `test/` 目录下且命名为 `test_*.py`（配置见 `pytest.ini`）。
- **Windows 下中文乱码**：终端执行 `chcp 65001` 切 UTF-8；代码文件统一 UTF-8 编码保存（VS Code 右下角可确认）。
- **本地有一堆 CRLF 改动**：仓库已通过 `.gitattributes` 统一为 LF；若仍有大量假改动，执行 `git config --global core.autocrlf false` 后重新 clone。

## 8. 相关文档

| 文档 | 内容 |
| --- | --- |
| `docs/plan.md` | 分工、里程碑、协作节奏、风险清单 |
| `docs/interface.md` | **接口契约**（棋盘表示、Move 结构、各模块函数签名） |
| `docs/setup.md` | 环境搭建、常见 Git 操作图文步骤 |
| `docs/tasks/` | **任务派发与模块任务书（队友从这里领活）** |
| `docs/meeting/` | 会议记录 |
| `README.md` | 项目简介、快速开始、进度 |

## 附：给新成员的一页速查

```bash
git checkout dev && git pull origin dev      # 1. 同步
git checkout -b feature/xxx                  # 2. 开分支
# ...写代码...
pytest -q && python main.py                  # 3. 自测
git add . && git commit -m "feat(rule): xxx" # 4. 提交
git push origin feature/xxx                  # 5. 推送
# 6. 网页上向 dev 提 PR，等 CI 绿，再 @ 组长合并
```
