# 环境搭建与常用 Git 操作

> 面向第一次参与团队项目的同学，按顺序做一遍即可。协作规范见 `CONTRIBUTING.md`。

## 1. 安装工具

| 工具 | 说明 |
| --- | --- |
| Python 3.9+ | 安装时**勾选 Add Python to PATH**；用 `python --version` 验证 |
| Git for Windows | 安装后 `git --version` 验证 |
| VS Code（推荐） | 装 Python 插件；右下角确认文件编码为 UTF-8 |

## 2. 首次配置 Git（只需一次）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱@example.com"   # 建议与 GitHub 账号一致
git config --global core.autocrlf false                  # 仓库已用 .gitattributes 统一 LF
git config --global init.defaultBranch main
git config --global pull.rebase true                     # 拉取默认 rebase，历史更干净
```

## 3. 克隆并准备环境

```bash
git clone https://github.com/wyhsy/-amazon-chess-.git
cd "-amazon-chess-"            # 仓库名首尾带连字符，必须加引号

git checkout -b dev origin/dev  # 本地 dev 跟踪远程 dev

python -m venv .venv
.venv\Scripts\Activate.ps1      # Windows PowerShell（CMD 用 .venv\Scripts\activate.bat）
# source .venv/bin/activate     # macOS / Linux

pip install -r requirements-dev.txt
pytest -q                       # 能跑起来就说明环境 OK
```

> PowerShell 若报"禁止运行脚本"，执行一次：
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`

## 4. 每天的开始与结束

```bash
# 开始
git checkout dev
git pull origin dev
git checkout feature/你的分支
git rebase dev            # 把 dev 的最新改动叠到你的分支上

# 结束（未完成也要提交，避免丢代码）
git add -A
git commit -m "wip(rule): 走法生成框架（未完成）"
git push origin feature/你的分支
```

## 5. 查看状态与时机的常用命令

```bash
git status                      # 当前改动
git log --oneline -10           # 最近 10 条提交
git log --oneline --graph --all # 图形化分支历史
git diff                        # 未暂存的改动
git diff --staged               # 已暂存的改动
git branch -vv                  # 本地分支与跟踪关系
git fetch --prune               # 清理已删除的远程分支引用
git remote -v                    # 确认远端地址
```

## 6. 撤销与回退（谨慎使用）

```bash
# 撤销某个文件的未提交改动
git restore rule.py

# 取消暂存（保留工作区改动）
git restore --staged rule.py

# 修改上一条提交信息
git commit --amend -m "feat(rule): 修正提交信息"

# 回退到某个提交（本地未推送时）
git reset --hard <commit-sha>          # 丢弃之后的所有改动，慎用
git reset --soft HEAD~1                # 撤销提交但保留改动在暂存区
```

> 已经推到远程的提交不要用 `reset --hard` 后强推共享分支（`dev`、`main` 绝对禁止）。

## 7. 冲突解决实操

现象：`git rebase dev` 或 PR 页面上提示 `CONFLICT (content): Merge conflict in rule.py`

1. 打开冲突文件，会看到：

```text
<<<<<<< HEAD
        # 你的改动
=======
        # dev 上的改动
>>>>>>> dev
```

2. 与对方确认后手工改成最终版本，**删除 `<<<<<<<`、`=======`、`>>>>>>>` 三行标记**。
3. 继续：

```bash
git add rule.py
git rebase --continue
# 不想继续了：git rebase --abort
```

4. 重新推送自己的分支：`git push --force-with-lease origin feature/你的分支`

> 冲突涉及别人负责的文件时，不要自己拍板实现方式，先 @ 对方。

## 8. 提交前的自检清单

```bash
git status          # 只看应该改的文件
pytest -q           # 全绿
python main.py      # 相关路径能跑
```

确认没有 `__pycache__/`、`.venv/`、本地截图、日志文件被 `git add`。

## 9. 常见报错对照表

| 报错 | 原因 | 处理 |
| --- | --- | --- |
| `remote: error: GH006: Protected branch update failed` | 直推了 `main`/`dev` | 正常，改走 PR 流程 |
| `Updates were rejected because the remote contains work...` | 远程有新提交 | 先 `git pull --rebase`，再 push |
| `ModuleNotFoundError: pygame` | 未激活虚拟环境 / 未装依赖 | 激活 `.venv` 后 `pip install -r requirements-dev.txt` |
| `no tests ran` | 测试文件位置或命名不符 | 放 `test/` 下，命名 `test_*.py` |
| 报错信息出现乱码 | 终端编码非 UTF-8 | `chcp 65001`（Windows）；文件另存为 UTF-8 |
| `fatal: not a git repository` | 不在项目目录 | `cd` 到仓库根目录（注意加引号） |
| 大量无意义的整文件改动 | CRLF/LF 混乱 | `git config --global core.autocrlf false` 后重新 clone |

## 10. VSCode 推荐设置（可选）

`.vscode/settings.json` 已被 `.gitignore` 忽略，个人喜好放这里即可：

```json
{
  "files.encoding": "utf8",
  "files.eol": "\\n",
  "[python]": { "editor.formatOnSave": true },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["test"]
}
```
