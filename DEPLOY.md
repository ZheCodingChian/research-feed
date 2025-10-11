# Deployment Guide

Complete guide for deploying the Research Feed system to production on a VPS.

---

## Architecture Overview

The system consists of three components:

1. **Frontend** (GitHub Pages) - Static React app hosted for free
2. **Backend Server** (VPS) - Node.js Express API running 24/7 in Docker with PM2
3. **Data Pipeline** (VPS) - Python script running daily via cron to update the database

**Key Integration:** Both server and pipeline share a SQLite database via a Docker volume.

---

## Prerequisites

- DigitalOcean Droplet (or any VPS) - Minimum 2GB RAM, 1 vCPU
- Ubuntu 22.04 LTS (recommended)
- Domain name (optional, for custom URL)
- SSH access to VPS

---

## Part 1: VPS Initial Setup

### 1.1 SSH into VPS

```bash
ssh root@your-vps-ip
```

### 1.2 Set Timezone to SGT

```bash
timedatectl set-timezone Asia/Singapore
timedatectl  # Verify timezone is set correctly
```

### 1.3 Update System

```bash
apt update && apt upgrade -y
```

### 1.4 Install Docker

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

### 1.5 Install Git

```bash
apt install git -y
```

---

## Part 2: Clone Repository and Setup

### 2.1 Clone Repository

```bash
cd /root  # Or your preferred location
git clone https://github.com/yourusername/research-feed.git
cd research-feed
```

### 2.2 Create Pipeline .env File

```bash
nano pipeline/.env
```

Paste your environment variables (API keys, etc.):
```
OPENAI_API_KEY=your_key_here
# Add other env vars as needed
```

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

---

## Part 3: Database Initialization

### 3.1 Upload Database to VPS

**From your local machine:**

```bash
# Upload the database file to VPS
scp pipeline/database.sqlite root@your-vps-ip:/tmp/database.sqlite
```

### 3.2 Create Docker Volume and Copy Database

**On VPS:**

```bash
cd /root/research-feed

# Create the Docker volume
docker volume create research-feed_db-data

# Copy database into the volume
docker run --rm \
  -v research-feed_db-data:/data \
  -v /tmp:/host \
  alpine cp /host/database.sqlite /data/database.sqlite

# Verify the database is in the volume
docker run --rm -v research-feed_db-data:/data alpine ls -lh /data/
```

You should see `database.sqlite` listed.

### 3.3 Clean Up Temp File

```bash
rm /tmp/database.sqlite
```

---

## Part 4: Build and Start Services

### 4.1 Build Docker Images

```bash
cd /root/research-feed
docker-compose build
```

This will build both the `server` and `pipeline` images.

### 4.2 Start the Server

```bash
docker-compose up -d server
```

### 4.3 Verify Server is Running

```bash
# Check container status
docker-compose ps

# Check server logs
docker-compose logs -f server

# Test health endpoint
curl http://localhost:3001/api/health
```

You should see:
```json
{
  "success": true,
  "message": "Research Feed API is running",
  "timestamp": "2025-10-11T..."
}
```

### 4.4 Test API Endpoints

```bash
# Get papers metadata
curl http://localhost:3001/api/papers/metadata

# Get papers (with pagination)
curl "http://localhost:3001/api/papers?limit=10&offset=0"
```

---

## Part 5: Cron Job Setup (Daily Pipeline Run)

### 5.1 Test Pipeline Manually First

```bash
cd /root/research-feed

# Run pipeline once manually
docker-compose run --rm pipeline
```

This will:
- Process papers from 15 days ago
- Update the database
- Exit when complete

**Check logs:**
```bash
cat pipeline/logs/$(date +%Y%m%d).log
```

### 5.2 Reload Server to Pick Up New Data

```bash
docker-compose exec server pm2 reload all
```

Verify the server reloaded successfully:
```bash
docker-compose logs server --tail 20
```

### 5.3 Set Up Cron Job

```bash
crontab -e
```

Add this line (runs daily at 7:00 AM SGT):

```cron
0 7 * * * cd /root/research-feed && docker-compose run --rm pipeline && docker-compose exec -T server pm2 reload all >> /var/log/research-feed-pipeline-cron.log 2>&1
```

**Explanation:**
- `0 7 * * *` - Run at 7:00 AM every day
- `cd /root/research-feed` - Navigate to project directory
- `docker-compose run --rm pipeline` - Run pipeline, remove container after exit
- `docker-compose exec -T server pm2 reload all` - Gracefully reload server
- `>> /var/log/research-feed-pipeline-cron.log 2>&1` - Log cron output

Save and exit.

### 5.4 Verify Cron Job

```bash
# List cron jobs
crontab -l

# Check cron service is running
systemctl status cron
```

---

## Part 6: Networking (Optional - Expose API to Internet)

### Option A: Direct Port Exposure (Simple, No SSL)

**Update docker-compose.yml ports:**
```yaml
ports:
  - "0.0.0.0:3001:3001"  # Expose to all interfaces
```

Restart server:
```bash
docker-compose up -d server
```

API is now accessible at: `http://your-vps-ip:3001`

### Option B: Nginx Reverse Proxy with SSL (Recommended)

**Install Nginx:**
```bash
apt install nginx certbot python3-certbot-nginx -y
```

**Create Nginx config:**
```bash
nano /etc/nginx/sites-available/arxiv-api
```

**Add configuration:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Enable site:**
```bash
ln -s /etc/nginx/sites-available/arxiv-api /etc/nginx/sites-enabled/
nginx -t  # Test configuration
systemctl restart nginx
```

**Get SSL certificate:**
```bash
certbot --nginx -d api.yourdomain.com
```

API is now accessible at: `https://api.yourdomain.com`

---

## Part 7: Frontend Configuration

### 7.1 Update Frontend API URL

In your frontend repository, update the API endpoint:

```javascript
// frontend/src/config.js (or wherever you store API config)
const API_BASE_URL = 'https://api.yourdomain.com';  // Or http://your-vps-ip:3001
```

### 7.2 Deploy Frontend to GitHub Pages

```bash
# In your frontend directory
npm run build
npm run deploy  # Or your GitHub Pages deployment command
```

---

## Part 8: Monitoring and Maintenance

### 8.1 View Logs

**Server logs:**
```bash
docker-compose logs -f server
```

**Pipeline logs:**
```bash
# Latest run
cat pipeline/logs/$(date +%Y%m%d).log

# Specific date
cat pipeline/logs/20251011.log

# Cron job logs
tail -f /var/log/research-feed-pipeline-cron.log
```

**PM2 logs (inside container):**
```bash
docker-compose exec server pm2 logs
```

### 8.2 Check Service Status

```bash
# Docker containers
docker-compose ps

# Server health
curl http://localhost:3001/api/health

# PM2 status
docker-compose exec server pm2 status
```

### 8.3 Restart Services

**Restart server:**
```bash
docker-compose restart server
```

**Graceful reload (zero downtime):**
```bash
docker-compose exec server pm2 reload all
```

---

## Part 9: Updating Code

### 9.1 Pull Latest Changes

```bash
cd /root/research-feed
git pull origin main
```

### 9.2 Rebuild and Restart

**If pipeline code changed:**
```bash
docker-compose build pipeline
# No restart needed - will use new image on next cron run
```

**If server code changed:**
```bash
docker-compose build server
docker-compose up -d server
```

**If both changed:**
```bash
docker-compose build
docker-compose up -d server
```

---

## Part 10: Troubleshooting

### Issue: Server won't start

**Check logs:**
```bash
docker-compose logs server
```

**Common causes:**
- Database volume not mounted: Verify with `docker volume ls`
- Port 3001 already in use: `lsof -i :3001`
- Missing dependencies: Rebuild image with `docker-compose build server`

### Issue: Pipeline fails

**Check logs:**
```bash
cat pipeline/logs/$(date +%Y%m%d).log
```

**Common causes:**
- Missing `.env` file: Ensure `pipeline/.env` exists
- Database permissions: Volume should be mounted with `:rw`
- Insufficient memory: Check VPS RAM usage with `free -h`

### Issue: Cron job not running

**Check cron status:**
```bash
systemctl status cron
cat /var/log/research-feed-pipeline-cron.log
```

**Test cron command manually:**
```bash
cd /root/research-feed && docker-compose run --rm pipeline
```

### Issue: Database not updating

**Check atomic swap:**
```bash
# Inside a pipeline run, check if database.new.sqlite is created
docker-compose run --rm pipeline
# After run, verify database was updated
docker run --rm -v research-feed_db-data:/data alpine ls -lh /data/
```

### Issue: Server shows old data after pipeline run

**Reload server:**
```bash
docker-compose exec server pm2 reload all
```

**Check if server reopened DB connection:**
```bash
docker-compose logs server --tail 50
# Should see "Connected to SQLite database" after reload
```

---

## Part 11: Backup and Recovery

### 11.1 Backup Database

```bash
# Backup from Docker volume
docker run --rm \
  -v research-feed_db-data:/data \
  -v /root/backups:/backup \
  alpine cp /data/database.sqlite /backup/database-$(date +%Y%m%d).sqlite

# Download to local machine
scp root@your-vps-ip:/root/backups/database-20251011.sqlite ./
```

### 11.2 Restore Database

```bash
# Upload backup to VPS
scp ./database-backup.sqlite root@your-vps-ip:/tmp/

# Restore to volume
docker run --rm \
  -v research-feed_db-data:/data \
  -v /tmp:/host \
  alpine cp /host/database-backup.sqlite /data/database.sqlite

# Reload server
docker-compose exec server pm2 reload all
```

---

## Quick Reference Commands

### Daily Operations
```bash
# View server logs
docker-compose logs -f server

# View pipeline logs
cat pipeline/logs/$(date +%Y%m%d).log

# Manually run pipeline
docker-compose run --rm pipeline

# Reload server
docker-compose exec server pm2 reload all

# Check API health
curl http://localhost:3001/api/health
```

### Debugging
```bash
# Shell into server container
docker-compose exec server sh

# Shell into pipeline container (while running)
docker-compose run --rm --entrypoint sh pipeline

# View PM2 status
docker-compose exec server pm2 status

# View Docker volumes
docker volume ls
docker volume inspect research-feed_db-data
```

---

## Security Recommendations

1. **Firewall:** Only expose necessary ports (80, 443, 22)
   ```bash
   ufw allow 22/tcp
   ufw allow 80/tcp
   ufw allow 443/tcp
   ufw enable
   ```

2. **SSH:** Use key-based authentication, disable password login

3. **Environment variables:** Never commit `.env` files to Git

4. **Updates:** Regularly update system packages
   ```bash
   apt update && apt upgrade -y
   ```

5. **Monitoring:** Set up alerts for service downtime (UptimeRobot, etc.)

---

## Support

For issues or questions:
- Check logs first (server, pipeline, cron)
- Review this deployment guide
- Check GitHub repository issues

---

**Last Updated:** 2025-10-11
