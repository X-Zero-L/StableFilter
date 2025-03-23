# StableFilter

[English](README_EN.md) | 简体中文

StableFilter 是一个用于对稳定扩散模型标签进行智能分类的工具。它能够自动将标签分类为不同安全级别，并提供详细的中文解释和翻译。

## 功能特点

- 智能标签分类：将标签分为 general、sensitive、nsfw、explicit 四个安全级别
- 并发处理：支持高并发处理大量标签
- 断点续传：支持中断后继续处理
- 详细解释：为每个分类提供详细的中文解释
- 中文翻译：提供准确的中文翻译

## 安装

1. 克隆仓库：

```bash
git clone https://github.com/X-Zero-L/StableFilter.git
cd StableFilter
```

2. 安装环境：

```bash
uv sync
```

3. 配置环境变量：

```bash
cp .env.example .env
# 编辑 .env 文件，填入必要的配置信息
```

## 使用方法

如果只是想使用已经分类好的标签数据，可以在本项目的 release 页面下载。

1. 准备标签数据：

   - 将需要分类的标签放在 `selected_tags.csv` 文件中
   - CSV 文件应包含 `name` 列

2. 运行分类程序：

```bash
uv run -m src.main
```

3. 查看结果：
   - 分类结果将保存在 `results/tag_classifications.json` 文件中
   - 可以随时中断程序，下次运行时会自动继续处理未完成的标签

## 项目结构

```
StableFilter/
├── src/
│   ├── core/           # 核心功能实现
│   ├── models/         # 数据模型定义
│   ├── utils/          # 工具函数
│   └── config/         # 配置文件
├── tests/              # 测试用例
├── docs/               # 文档
├── results/            # 结果输出目录
└── tag_groups/         # 标签分组数据
```

## 许可证

MIT License
