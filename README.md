# prelegal

A web application built with a FastAPI (Python) backend and a Next.js (TypeScript/React) frontend.

## Tech Stack

- **Backend:** [FastAPI](https://fastapi.tiangolo.com/) (Python)
- **Frontend:** [Next.js](https://nextjs.org/) (React + TypeScript)

## Project Structure

```
prelegal/
├── backend/      # FastAPI application
└── frontend/     # Next.js application
```

## Getting Started

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`. Interactive docs at `http://localhost:8000/docs`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The web app will be available at `http://localhost:3000`.

## Environment Variables

Copy `.env.example` to `.env.local` (frontend) and `.env` (backend) and fill in the required values.

## License

[MIT](LICENSE)
