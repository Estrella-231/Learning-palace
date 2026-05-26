# Learning Palace

一个使用 Next.js + FastAPI 构建的 AI 学习助手，支持知识图谱可视化和 Markdown 渲染。

## 技术栈

### Frontend
- **Next.js 14** - React 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 样式
- **ReactFlow** - 知识图谱可视化
- **Zustand** - 状态管理
- **KaTeX** - 数学公式渲染

### Backend
- **FastAPI** - Web 框架
- **SQLAlchemy** - ORM
- **PostgreSQL + pgvector** - 向量数据库
- **Anthropic/OpenAI** - AI 模型集成

## 快速开始

### 前置条件
- Python 3.11+
- Node.js 18+
- PostgreSQL 16+

### 1. 克隆项目
```bash
git clone https://github.com/Estrella-231/Learning-palace.git
cd Learning-palace
```

### 2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env，填入你的 API Key
```

### 3. 启动后端
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 4. 启动前端
```bash
cd frontend
npm install
npm run dev
```

### 5. 使用 Docker (可选)
```bash
docker-compose up -d
```

## 配置说明

### 数据库配置
在 `config.json` 中配置数据库连接参数。

### API Keys
支持多种 AI API（至少需要一个）：
- `ANTHROPIC_API_KEY` - Claude
- `OPENAI_API_KEY` - GPT
- `OPENROUTER_API_KEY` - OpenRouter
- `DEEPSEEK_API_KEY` - DeepSeek

## 项目结构

```
learning-palace/
├── frontend/          # Next.js 前端
│   ├── src/
│   │   └── ...        # 组件和页面
│   └── package.json
├── backend/           # FastAPI 后端
│   ├── app/
│   │   ├── models/    # 数据模型
│   │   ├── routers/   # API 路由
│   │   ├── schemas/   # Pydantic 模型
│   │   ├── services/  # 业务逻辑
│   │   └── main.py   # 入口文件
│   └── requirements.txt
├── docker-compose.yml
└── config.json
```

## License

MIT