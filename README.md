# Learning Palace

Learning Palace 是一个 AI 学习助手项目，用 Next.js 和 FastAPI 构建。它可以围绕课程内容进行对话、抽取知识点、生成知识图谱，并通过复习卡片帮助用户巩固概念。

## 功能亮点

- 课程与知识点管理
- AI 对话式学习助手
- 知识图谱可视化
- 节点详情与相关概念查看
- 复习卡片与学习进度追踪
- Markdown 与数学公式渲染
- 支持多种 LLM Provider 配置

## 技术栈

**Frontend**

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- React Flow
- Zustand
- KaTeX / react-markdown

**Backend**

- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Pydantic Settings
- Anthropic / OpenAI / OpenAI-compatible APIs

## 项目结构

```text
learning-palace/
├── backend/
│   ├── app/
│   │   ├── models/      # SQLAlchemy models
│   │   ├── prompts/     # LLM prompts
│   │   ├── routers/     # FastAPI routes
│   │   ├── schemas/     # Pydantic schemas
│   │   ├── services/    # LLM, extraction, merge, review services
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/         # Next.js app routes
│   │   ├── components/  # UI components
│   │   ├── lib/         # API client
│   │   ├── stores/      # Zustand stores
│   │   └── types/
│   └── package.json
├── config.json          # Model and database configuration
├── docker-compose.yml   # PostgreSQL + pgvector
└── README.md
```

## 快速开始

### 1. 准备环境

需要先安装：

- Python 3.11+
- Node.js 18+
- Docker Desktop 或本地 PostgreSQL 16+

### 2. 克隆仓库

```bash
git clone https://github.com/Estrella-231/Learning-palace.git
cd Learning-palace
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

然后编辑 `.env`，至少填入一个可用的模型 API Key。如果使用默认的 MiniMax Anthropic 配置，需要设置：

```bash
LP_API_KEY=your_api_key_here
```

如果要使用 OpenAI embedding，还需要设置：

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

模型、Provider、base URL 和数据库连接都可以在 `config.json` 中调整。

### 4. 启动数据库

```bash
docker compose up -d
```

这会启动一个带 pgvector 的 PostgreSQL 16 实例：

- Host: `localhost`
- Port: `5432`
- Database: `learning_palace`
- User: `postgres`
- Password: `postgres`

### 5. 启动后端

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

后端健康检查：

```bash
curl http://localhost:8000/api/health
```

### 6. 启动前端

打开新的终端：

```bash
cd frontend
npm install
npm run dev
```

访问：

```text
http://localhost:3000
```

## 常用命令

```bash
# 启动数据库
docker compose up -d

# 停止数据库
docker compose down

# 后端开发服务
cd backend && uvicorn app.main:app --reload --port 8000

# 前端开发服务
cd frontend && npm run dev

# 前端构建
cd frontend && npm run build
```

## 配置说明

`config.json` 里默认包含以下模型配置：

- `minimax-anthropic`
- `minimax`
- `claude`
- `openai`
- `openrouter`
- `deepseek`

默认模型由：

```json
{
  "models": {
    "default": "minimax-anthropic"
  }
}
```

控制。你可以把它改成其他已配置的模型名称。

数据库连接默认是：

```text
postgresql+asyncpg://postgres:postgres@localhost:5432/learning_palace
```

## API

后端启动后，FastAPI 文档可以在这里查看：

```text
http://localhost:8000/docs
```

主要接口前缀为 `/api`，包括：

- `/api/health`
- `/api/chat`
- `/api/courses`
- `/api/nodes`
- `/api/map`
- `/api/review`

## License

MIT
