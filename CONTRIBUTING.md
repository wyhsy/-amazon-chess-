```
# 贡献指南（CONTRIBUTING）
本文档规定 `-amazon-chess-` 项目的团队协作开发流程，所有参与开发的成员请严格遵循本规范。

## 1. 前置准备
### 1.1 接受仓库邀请
1. 登录 GitHub 账号，点击右上角通知铃铛图标
2. 找到 `-amazon-chess-` 仓库的协作者邀请，点击 **Accept invitation** 完成接受
3. 接受后将获得仓库 Write 权限，可正常推送代码、发起合并请求

### 1.2 本地仓库初始化（仅首次操作）
```bash
# 克隆远程仓库到本地
git clone https://github.com/wyhsy/-amazon-chess-.git

# 进入项目目录（Windows PowerShell 需加引号）
cd "-amazon-chess-"

# 拉取远程全部分支信息
git fetch origin

# 创建本地 dev 分支并关联远程 dev 分支
git checkout -b dev origin/dev
```

执行 `git branch` 命令，输出同时包含 `main` 和 `dev` 即配置完成。

## 2. 分支管理规范

项目采用三类分支体系：

表格

| 分支类型 | 分支名 | 作用 | 操作权限 |
| --- | --- | --- | --- |
| 主分支 | `main` | 存放稳定可运行的版本，用于里程碑发布、答辩演示 | 禁止直接提交，仅从 `dev` 合并 |
| 开发分支 | `dev` | 团队统一开发集成分支，所有功能代码最终汇合于此 | 不允许直接推送，功能分支通过 PR 合并 |
| 功能分支 | `feature/模块名` | 单个功能开发的临时分支，开发完成后删除 | 开发者自行创建、提交、推送 |

### 功能分支命名参考

- 规则引擎模块：`feature/rule-engine`
- UI 界面模块：`feature/ui-pygame`
- AI 搜索算法：`feature/ai-search`
- 估值函数与文档：`feature/eval-docs`

## 3. 日常开发工作流

每次开发新功能，严格按照以下流程执行：

### 步骤 1：同步最新代码

每次开工前，务必先拉取远程最新的 dev 代码，减少合并冲突：

```
git checkout dev
git pull origin dev
```

### 步骤 2：创建功能分支

从最新的 `dev` 分支创建自己的功能分支：

```
git checkout -b feature/模块名
```

### 步骤 3：编写代码并本地提交

功能开发完成后，提交代码到本地分支：

```
# 添加所有修改的文件
git add .

# 提交代码，填写规范的提交信息
git commit -m "feat: 实现棋子移动合法性判断"
```

### 步骤 4：推送到远程仓库

```
git push origin feature/模块名
```

### 步骤 5：发起 Pull Request（PR）

1. 打开 GitHub 仓库页面，顶部会自动出现「Compare & pull request」提示
2. 源分支选择你的功能分支，目标分支选择 **`dev`**
3. 填写 PR 标题与描述，说明本次完成的功能、测试情况
4. 提交 PR，等待组长审核合并

### 步骤 6：合并完成，清理分支

PR 成功合并进 dev 后，在本地清理已完成的功能分支：

```
# 切回 dev 分支，拉取合并后的最新代码
git checkout dev
git pull origin dev

# 删除本地已完成的功能分支
git branch -d feature/模块名
```

## 4. 提交信息规范

Commit 信息统一采用 `类型: 描述内容` 的格式：

表格

| 类型标识 | 说明 |
| --- | --- |
| `feat` | 新增功能 |
| `fix` | 修复 Bug |
| `docs` | 文档、README 变更 |
| `refactor` | 代码重构，不改变功能逻辑 |
| `style` | 代码格式调整，不影响运行逻辑 |
| `test` | 新增或修改测试代码 |

**示例：**

```
feat: 生成全部合法走法
fix: 修复游戏结束判定错误
docs: 更新贡献指南文档
```

## 5. 代码冲突处理

1. 先执行 `git pull origin dev` 拉取远程最新的 dev 代码
2. 在本地编辑器中打开冲突文件，手动合并冲突内容
3. 冲突解决完成后，执行 `git add .` + `git commit` 提交合并结果
4. 再正常推送代码、发起 PR

## 6. 协作红线（必须遵守）

1. **绝对禁止直接向 main、dev 分支推送代码**，所有改动必须通过 PR 合并
2. 仅修改自己负责的模块文件，不随意改动他人负责的代码
3. 一个功能分支只完成一件事，不混合多个无关功能
4. 提交信息清晰明确，禁止仅使用「更新」「修改」等模糊描述
5. 出现代码冲突必须在本地解决完成后，再提交 PR

## 7. 常见问题

- **连接失败 / Connection reset**：GitHub 国内网络不稳定，可多次重试；持续失败可切换 Gitee 镜像
- **分支已存在报错**：本地已有同名分支时，直接使用 `git checkout 分支名` 切换即可

```

## 二、创建文件并推送到 GitHub
### 推荐方式：手动创建 + 命令提交（最稳妥，不会乱码）
1. 打开 `-amazon-chess-` 文件夹
2. 右键 → 新建 → 文本文档，重命名为 `CONTRIBUTING.md`（注意后缀是 `.md`，不是 `.txt`）
3. 用记事本/VSCode打开文件，粘贴上面的完整内容，保存
4. 回到 PowerShell，依次执行：
```powershell
# 确保在项目根目录
cd "-amazon-chess-"

# 切换到 main 分支（文档更新直接放主分支即可）
git checkout main

# 添加文件到暂存区
git add CONTRIBUTING.md

# 提交变更
git commit -m "docs: 添加团队协作贡献指南 CONTRIBUTING.md"

# 推送到远程仓库
git push origin main
```
