# Atlas AI: Deployment Guide (Vercel Serverless)

Atlas is fully decoupled and optimized to run entirely on serverless infrastructure. Instead of managing long-running background processes or traditional Ubuntu VMs, you push code directly to Vercel.

## 1. Prerequisites

1. A Vercel Account linked to your GitHub repository.
2. A Supabase project (providing the PostgreSQL database).
3. Groq API Keys.

## 2. Serverless Backend Configuration

We removed `apscheduler` so the Python application operates dynamically.

### Vercel App Setup (Backend)
1. In Vercel, import the `backend/` directory of the repository (or the root and define `backend` as the Root Directory).
2. The framework preset is **Other**.
3. Vercel utilizes the `vercel.json` file automatically:
```json
{
    "version": 2,
    "builds": [
        {
            "src": "api/main.py",
            "use": "@vercel/python"
        }
    ],
    "routes": [
        {
            "src": "/(.*)",
            "dest": "api/main.py"
        }
    ]
}
```

### Environment Variables (Vercel Backend Settings)
Add these accurately to the Vercel dashboard:
- `SUPABASE_URL`
- `SUPABASE_KEY` (Service role key)
- `GROQ_API_KEY`
- `CRON_SECRET` (A strong random string. Example: `ab849hf02hf893hf`)

## 3. Configuring Auto-Reasoning (Vercel Cron)

Because Atlas is serverless, the AI agents are woken up by HTTP requests rather than internal loops.

Next to the `backend/vercel.json`, Vercel reads a `vercel.json` (or you can merge them) configuration for cron.
Ensure your cron config looks like this in the deployed environment to trigger the actual intelligence:

```json
{
  "crons": [
    {
      "path": "/tasks/sentinel",
      "schedule": "*/5 * * * *"
    },
    {
      "path": "/tasks/heartbeat",
      "schedule": "*/30 * * * *"
    },
    {
      "path": "/tasks/morning-brief",
      "schedule": "0 7 * * *"
    }
  ]
}
```
*Note: Vercel automatically injects the `x-vercel-cron` header which our FastAPI app validates against `CRON_SECRET`.*

## 4. Frontend Deployment

1. Create a new Vercel project selecting the `frontend/` folder as the Root Directory.
2. Framework Preset: **Vite**.
3. **Environment Variable:** Set `VITE_API_URL` to the production URL of the backend you just deployed (e.g., `https://atlas-api.vercel.app`).
4. Since it uses Vite, Vercel will auto-detect the `npm run build` commands and serve out the `dist/` directory.

---

**You are live.** The frontend will automatically connect to the streaming API. Since you configured cron jobs on the backend, every 5 minutes your Supabase database will naturally accumulate new intelligence which immediately propagates to your deployed UI.
