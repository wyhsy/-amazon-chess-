```
# -amazon-chess-
亚马逊棋人机博弈课程设计项目 | 肆如破竹小组

## 项目简介
基于 Python + Pygame 开发的亚马逊棋（Amazon Chess）人机对战游戏，实现完整棋规、Minimax 博弈算法、Alpha-Beta 剪枝优化，支持人人对战与人机对战模式。

## 技术栈
- 编程语言：Python 3.9+
- 图形界面：Pygame
- 核心算法：Minimax + Alpha-Beta 剪枝
- 版本控制：Git + GitHub

## 目录结构
```

-amazon-chess-/
├── main.py              # 程序入口
├── board.py             # 棋盘数据模型
├── rule.py              # 规则引擎、走法生成
├── ui.py                # Pygame 界面交互
├── ai_search.py         # Minimax 搜索算法
├── ai_eval.py           # 局面估值函数
├── test/                # 单元测试
└── docs/                # 项目文档

```

## 环境搭建与运行
```bash
# 安装依赖
pip install pygame

# 运行游戏
python main.py
```
