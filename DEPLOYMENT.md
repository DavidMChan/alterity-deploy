# Deployment Guide for Alterity

This guide describes how to run the Alterity system (Web + Worker + DB).

## 1. Local Development (Automated)

We provide a `manage.sh` script to streamline local development.

### Setup
1. **Run**:
   ```bash
   ./manage.sh
   ```
   This will:
   - Check pre-requisites (Docker).
   - Create a `.env` file if missing.
   - Build and start the entire stack.
   - Output links to accessing services.

2. **Access**:
   - Web App: [http://localhost:3000](http://localhost:3000)
   - Studio: [http://localhost:8001](http://localhost:8001)

3. **Commands**:
   - `./manage.sh dev`  : Start stack
   - `./manage.sh logs` : View logs
   - `./manage.sh down` : Stop stack
   - `./manage.sh clean`: Stop and remove data

---

## 2. Production Deployment

For production, manage services separately.

### Architecture
- **Web**: Vercel or Cloud Container.
- **Worker**: Persistent Container (AWS, RunPod).
- **Database**: Supabase Cloud.

### Deployment Steps
1. **Database**: Create Supabase project and run `supabase/schema.sql`.
2. **Web**: Deploy `web` folder with Env Vars (Next.js).
3. **Worker**: Build and run Docker container:
   ```bash
   docker build -t alterity-worker ./worker
   docker run -d -e DATABASE_URL=... alterity-worker
   ```
