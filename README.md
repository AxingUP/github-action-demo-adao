# github-action-demo-adao
自动化获取AI相关的咨询信息

## 功能介绍

通过 GitHub Actions 定时任务，每天自动抓取过去24小时内的 AI 相关资讯，并翻译成中文。

- 定时触发：每天北京时间早上 7:00
- 手动触发：支持手动运行测试
- 数据源：OpenAI Blog、Google AI Blog、MIT Technology Review、Hacker News AI、The Verge AI
- 自动翻译：将英文资讯翻译成中文

## 使用方法

### 1. 克隆仓库

```bash
git clone https://github.com/AxingUP/github-action-demo-adao.git
cd github-action-demo-adao
```

### 2. 本地运行脚本

```bash
pip install -r requirements.txt
python scripts/fetch_ai_news.py
```

### 3. 查看 AI 资讯

生成的资讯报告保存在 `ai_news/` 目录下。

## 项目结构

```
.
├── .github/
│   └── workflows/
│       └── fetch-ai-news.yml    # GitHub Actions 工作流配置
├── config/
│   ├── sources.json              # 资讯源配置
│   └── keywords.txt             # AI 关键词列表
├── scripts/
│   └── fetch_ai_news.py          # Python 获取脚本
├── ai_news/                      # 生成的资讯报告
├── requirements.txt             # Python 依赖
└── README.md
```

## 配置说明

### 修改数据源

编辑 `config/sources.json`，添加或修改 RSS 源。

### 修改关键词

编辑 `config/keywords.txt`，添加或删除 AI 相关关键词。

## License

MIT License
