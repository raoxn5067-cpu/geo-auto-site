# GEO 自动发布站

一个基于 GitHub Actions + GitHub Pages 的每日自动发布系统，每天调用 OpenAI API 生成一篇面向 AI 搜索引擎（GEO）优化的文章，并自动部署上线。

## 特性

- 每天自动生成一篇 GEO 优化文章
- 静态站点（HTML），加载速度快，对搜索引擎友好
- 包含 Schema.org 结构化数据
- 支持问题型标题、核心结论、FAQ 等 GEO 元素
- 完全免费：GitHub Actions + GitHub Pages

## 项目结构

```
.
├── .github/workflows/daily-publish.yml  # 每日自动发布工作流
├── content/                             # 生成的 Markdown 文章
├── public/                              # 构建后的静态站点（自动上传部署）
├── src/
│   ├── data/topics.json                 # 内容主题库
│   ├── generate.py                      # 调用 OpenAI 生成文章
│   ├── build.py                         # 构建静态站点
│   └── templates/                       # Jinja2 HTML 模板
├── requirements.txt
└── README.md
```

## 快速开始

### 1. 创建 GitHub 仓库

1. 登录 GitHub，点击右上角 **+ → New repository**
2. 仓库名建议：`geo-auto-site`
3. 选择 **Public**
4. 不要勾选初始化 README（本仓库已有 README）
5. 创建后，把本项目的所有文件推送上去：

```bash
git init
git add .
git commit -m "init: GEO auto site"
git branch -M main
git remote add origin https://github.com/raoxn5067-cpu/geo-auto-site.git
git push -u origin main
```

### 2. 添加 OpenAI API Key

1. 打开仓库页面：`https://github.com/raoxn5067-cpu/geo-auto-site`
2. 点击 **Settings → Secrets and variables → Actions**
3. 点击 **New repository secret**
4. Name 填：`OPENAI_API_KEY`
5. Secret 填你的 OpenAI API Key
6. 点击 **Add secret**

### 3. 启用 GitHub Pages

1. 打开仓库 **Settings → Pages**
2. **Source** 选择 **GitHub Actions**
3. 保存

### 4. 手动触发第一次发布

1. 打开仓库 **Actions → Daily GEO Publish**
2. 点击 **Run workflow → Run workflow**
3. 等待几分钟后，访问页面：
   `https://raoxn5067-cpu.github.io/geo-auto-site/`

之后每天北京时间上午 10:00 会自动生成并发布新文章。

## 自定义

### 修改网站名称和描述

编辑 `src/build.py` 顶部的：

```python
SITE_NAME = "GEO 每日洞察"
SITE_DESCRIPTION = "面向 AI 搜索引擎的每日自动更新内容站"
```

### 修改内容主题

编辑 `src/data/topics.json` 中的 `topics` 数组，添加你自己的主题。系统每天会随机选取一个主题生成文章。

### 更换 AI 模型

编辑 `src/generate.py` 中的模型名称：

```python
model="gpt-4o-mini",  # 可改为 gpt-4o、deepseek-chat 等
```

如果使用 DeepSeek，需要把 `OpenAI` 客户端替换为 DeepSeek 兼容调用（base_url）。

## 费用说明

- GitHub Actions + GitHub Pages：免费（公开仓库）
- OpenAI API：每天一篇文章，使用 `gpt-4o-mini` 每月约 $0.5 - $2

## 许可证

MIT
