# LEAP Arcade — Deployment Guide

## Prerequisites

The following must be installed on the EC2 instance before you begin:

- Docker (with the Compose plugin — `docker compose`)
- Make
- Git (optional — only needed if cloning; not required if using the zip)

---

## Step 1 — Transfer the Repository

Copy the zip to the server and unpack it:

```bash
scp leap-5m-26.zip ec2-user@<EC2_IP>:~/
ssh ec2-user@<EC2_IP>
unzip leap-5m-26.zip
cd leap-5m-26
```

---

## Step 2 — Verify Environment Variables

The zip includes a pre-configured `backend/.env`. Open it and confirm the following values match what was agreed for the event:

| Variable | Description |
|---|---|
| `JWT_SECRET_KEY` | Secret used to sign player tokens |
| `EVENT_CODE` | Shared code players enter to join |
| `POSTGRES_PASSWORD` | Postgres password |

> **Note:** `POSTGRES_CONNECTION_STRING` in `backend/.env` is only used for local `uv run` commands. Docker Compose overrides it automatically to use the `postgres` service hostname — you do not need to edit it.

---

## Step 3 — Start the Stack

From the repository root:

```bash
make start
```

This runs `docker compose --env-file backend/.env up -d`, which:

1. Starts a PostgreSQL 16 container and waits for it to be healthy
2. Builds and starts the API container — runs database migrations automatically on startup, then seeds game content
3. Builds and starts the frontend container once the API is healthy

On first run, Docker will build the images. This takes a few minutes. Subsequent starts are fast.

---

## Step 4 — Verify

Check all three containers are running and healthy:

```bash
docker compose ps
```

You should see `postgres`, `api`, and `frontend` all in a `running` / `healthy` state.

Quick smoke test:

```bash
curl http://localhost:8000/health      # API health check
curl -I http://localhost:3000          # Frontend
```

---

## Step 5 — Open Firewall Ports

In the EC2 Security Group, allow inbound traffic on:

| Port | Service |
|------|---------|
| `3000` | Frontend (player-facing web app) |
| `8000` | API (optional — only if direct API access is needed) |

Players access the platform at `http://<EC2_PUBLIC_IP>:3000`.

---

## Stopping the Stack

```bash
make stop
```

This stops and removes the containers but **preserves the Postgres data volume** — player scores and sessions are retained.

To wipe all data and start completely fresh (e.g. for a re-run or clean reset):

```bash
# 1. Stop and remove containers, networks, and the Postgres volume
docker compose --env-file backend/.env down -v

# 2. Remove any dangling images from previous builds (optional but recommended)
docker image prune -f

# 3. Bring everything back up — re-seeds from scratch on startup
make start
```

If you also want to reclaim all unused Docker resources in one go (images, build cache, stopped containers):

```bash
docker system prune -af --volumes
make start
```

> **Warning:** `docker system prune --volumes` removes **all** unused volumes on the host, not just LEAP's. Only use it if this is a dedicated server.

---

## Troubleshooting

**Containers keep restarting**
```bash
docker compose logs api
docker compose logs frontend
```

**Database migrations failed**
```bash
docker compose logs api | grep -i alembic
```
The API container runs migrations automatically on startup via `scripts/migrate.sh`. If migrations fail, the API will not start. Check for connection errors — ensure Postgres is healthy before the API starts (Compose health-check dependency handles this, but on very slow instances you may need to retry `make start`).

**Port already in use**
Stop any existing services on ports 3000, 8000, or 5432 before starting.

---

## Open Questions for the Vendor

The following needs to be confirmed before the event. Please answer each question so we can finalise the setup.

**1. Cloud provider / hosting**
This guide assumes AWS EC2. Will you use a different cloud provider or hosting service (e.g. Azure, GCP, a bare-metal VM, a managed container service)? If so, please share the equivalent instance spec you plan to use so we can verify it meets the requirements.

**2. Participant access — domain vs. IP**
How will participants reach the platform?

- **Option A — Direct IP:** Participants access the app via `http://<server-ip>:3000`. No additional setup needed, but the URL is not user-friendly and there is no HTTPS.

- **Option B — Domain / subdomain with HTTPS:** You set up a domain or subdomain (e.g. `leap-arcade.example.com`), configure an nginx reverse proxy in front of port 3000, and provision an SSL certificate (e.g. via Let's Encrypt). This gives a clean URL and secure HTTPS but requires DNS and nginx configuration on your end.

Please confirm which option you will use, or propose an alternative. If Option B, let us know the intended domain so we can share it with participants in advance.

**3. Ongoing development and administration access**
This is version 1 of the platform. We will be iterating on it — adding new games, testing features, and pushing updates in the lead-up to the event. We therefore need a reliable way to deploy new builds and run operational commands (restart services, inspect logs, perform database resets) ourselves.

Will you provide us with SSH access to the host VM, or an equivalent mechanism such as a deployment pipeline we can trigger directly? If all changes must go through your team, please describe the process, expected turnaround, and how to reach you urgently on the day of the event itself.
