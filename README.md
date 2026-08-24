# Last-Mile Delivery Tracker

Full-stack delivery management platform implementing the supplied Last-Mile Delivery Tracker requirements.

**Stack:** FastAPI + async SQLAlchemy · PostgreSQL/SQLite · React + Vite + Tailwind · JWT auth

## Quick start

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python seed.py
uvicorn app.main:app --reload --port 8000
```
Swagger UI: `http://localhost:8000/docs`

Demo accounts:
- Admin: `admin@lastmile.com` / `admin123`
- Agent: `agent1@lastmile.com` / `agent123`
- Agent: `agent2@lastmile.com` / `agent123`
- Customer: `customer@lastmile.com` / `customer123`

### Frontend
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

## Requirements covered

- Customer registration/login and admin-created customer orders.
- Admin-managed pincode-to-zone mappings and B2B/B2C intra/inter-zone rate cards.
- Volumetric weight `(L × B × H) / 5000`, chargeable weight as the higher of actual/volumetric, configured minimums, and COD surcharge.
- Pre-confirmation charge estimate using the same calculation path as order creation.
- Manual or automatic agent assignment with availability/capacity checks and zone/load/distance ranking.
- Explicit order lifecycle with append-only tracking history, actor and timestamp.
- Failed-delivery notifications, rescheduling, and fresh agent assignment.
- Email notifications on every status change plus optional Twilio SMS.
- Admin order filtering and status override.

## Deployment

The backend includes a Render blueprint and Dockerfile; the frontend includes Vercel SPA routing. A hosted application URL was not supplied or deployed by this task, so none is claimed here.

## Testing

Run `cd backend && pytest -q`. Core tests cover volumetric-weight calculation and the lifecycle state machine. Full API integration tests require the dependencies in `backend/requirements.txt`.

See `system-design.md` for the requested architecture write-up.
