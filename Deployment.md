# Deployment Guide: Atlas Zero on Vercel

Atlas Zero is designed to be deployed as two separate services (Frontend and Backend) within a single repository. This ensures the frontend stays fast and the backend reasoning engines are managed by Vercel Cron.

## 1. Backend Deployment (FastAPI)

### Setup
1. Create a new project in Vercel.
2. Link your repository.
3. **Important**: Set the **Root Directory** to `backend`.
4. Select **Python** as the framework (Vercel should detect this automatically via `requirements.txt`).

### Environment Variables
Configure the following in the Vercel Dashboard:
- `SUPABASE_URL`: Your Supabase project URL.
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key.
- `GROQ_API_KEY`: Groq API key for LLM reasoning.
- `OPENAI_API_KEY`: OpenAI API key for embeddings.
- `CORS_ORIGINS`: The URL of your **Frontend** deployment (e.g., `https://atlas-zero-frontend.vercel.app`).
- `CRON_SECRET`: A secret string (e.g., `atlas_cron_secret_123`) that matches the one in your `backend/api/routers/tasks.py` (or set a new one).

### Cron Jobs
Vercel will automatically detect the cron schedules in `backend/vercel.json`. You can monitor these in the **Cron** tab of your project settings.

---

## 2. Frontend Deployment (React/Vite)

### Setup
1. Create a *second* project in Vercel.
2. Link the same repository.
3. **Important**: Set the **Root Directory** to `frontend`.
4. Select **Vite** as the framework.

### Environment Variables
- `VITE_API_URL`: The URL of your **Backend** deployment (e.g., `https://atlas-zero-backend.vercel.app`).

---

## 3. Real-time (SSE) Considerations
Vercel's Serverless Functions have a maximum execution time (usually 10-60 seconds depending on your plan). 
- The intelligence stream (`/stream/live`) will disconnect when the function times out.
- The Atlas Zero frontend is built to automatically reconnect to the SSE stream. 
- In the dashboard, you may occasionally see a "SSE connection error" in the console, but the UI will recover and fetch the latest state upon reconnection.

---

## 4. Local Development
To run the project locally with the new task endpoints:
1. Start the backend: `uvicorn backend.api.main:app --reload`
2. Start the frontend: `npm run dev` (inside `frontend/`)
3. Test a task: `curl -H "X-Vercel-Cron: atlas_cron_secret_123" http://localhost:8000/tasks/sentinel`
