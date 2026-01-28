```markdown
# Health Plan Generator

A simple health goal planner application. Frontend uses React + TypeScript, backend is Python/Fasapi.

## Technologies

- Frontend: React, TypeScript
- Backend: Python, Fastapi, langchain

## Requirements

- Node.js (14+)
- `npm`
- Python 3.14+

## Installation

1. Backend

```bash
cd backend
uv sync (uv must have been installed and configured)
uvicorn main:app --reload
```

2. Frontend

```bash
cd frontend
npm install
npm run dev
# or
npm start
```

3. Environment variables

- Copy ` .env.example` to ` .env` if present and fill required values.

## Running

- Frontend typically runs at `http://localhost:3000`.
- Backend typically runs at `http://localhost:8000` (or according to your project settings).

## Tests

- Backend (if present):

```bash
cd backend
pytest tests
```

## Project structure (brief)

- `frontend/` — React application
- `backend/` — Python API
- `README.md` — Project description

## License

- Default: MIT (update if needed)

```
