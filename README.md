# Health Goal Planner

An AI-powered tool that helps users break down complex health goals into actionable weekly plans using LangGraph and
OpenAI.

## 🏗️ Architecture

```
┌─────────────┐
│   React +   │
│ TypeScript  │  Frontend: Chat UI + Plan Display
│  (Vite)     │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────┐
│   FastAPI   │  Backend: REST API + Database
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  LangGraph  │  Agent: Multi-step reasoning
│   Agent     │  (Understand → Clarify → Generate)
└──────┬──────┘
       │
       ▼
┌─────────────┐
│  OpenAI     │  LLM: GPT
│  GPT        │
└─────────────┘
       │
       ▼
┌─────────────┐
│   SQLite    │  Persistence: Goals + Plans
└─────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- OpenAI API Key

### Backend Setup

```bash
cd backend
uv sync (uv must have been installed and configured)

# Create .env file
echo "OPENAI_API_KEY=your_key_here" > .env

# Run server
uvicorn main:app --reload
```

Server runs on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

App runs on `http://localhost:5173`

### Run Tests

```bash
cd backend
pytest
```

## 🎨 Product Features (MVP)

✅ **Conversational Goal Input**

- Natural language goal description

✅ **Personalized 4-Week Plans**

- Week-by-week focus areas
- 3-5 specific tasks per week

✅ **Plan Persistence**

- Save goals and plans to database
- View previous goals
- Quick access to past plans

## 🔮 V2 Features (Future)

If I had more time, I would add:

1.**User Authentication**

- Proper login/signup flow
- Password reset, OAuth

2.**AI Coaching**

- Adaptive plans based on progress
- Motivational messages
- Obstacle troubleshooting

3.**Calendar Integration**

- Export to Google Calendar
- Reminder notifications

4.**Social Features**

- Share plans with friends
- Accountability partners
- Community challenges

## 🛠️ Tech Stack

**Frontend**:

- React 19 + TypeScript
- Vite (build tool)
- Tailwind CSS (styling)
- Axios (HTTP client)

**Backend**:

- FastAPI (Python web framework)
- LangChain + OpenAI (LLM integration)
- SQLite (database)

**Testing**:

- Pytest (backend tests)

## 🎥 Demo Script

- **Enter goal**: "I want to lose 15 kg"
- **Enter fitness level**: Beginner, None etc.
- **Generate plan**: Weekly structured breakdown
- **Show persistence**: See saved goals below

<video src="https://youtu.be/_gZ0zsnjuis" width="700" height="500" controls></video>

## 📄 License

MIT

---

