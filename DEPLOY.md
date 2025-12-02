# EC2 Deployment Guide

## Safe Deployment Workflow

### Step 1: SSH into EC2
```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
# or if you have it configured in ~/.ssh/config:
ssh viaduct-ec2
```

### Step 2: Navigate to Project Directory
```bash
cd viaductecho-backend
```

### Step 3: Stop Running Processes
```bash
# Find the running processes
ps aux | grep "python -m src"

# Kill them gracefully (replace PID with actual process IDs)
kill <PID_OF_API>
kill <PID_OF_AGGREGATOR>

# Or kill all Python processes (nuclear option - use carefully)
pkill -f "python -m src"

# Verify they're stopped
ps aux | grep "python -m src"
```

### Step 4: Backup Current Version (Optional but Recommended)
```bash
# Create a backup of the current working version
git branch backup-$(date +%Y%m%d-%H%M%S)

# Or create a tag
git tag backup-$(date +%Y%m%d-%H%M%S)
```

### Step 5: Pull Latest Code
```bash
# Fetch latest changes
git fetch origin

# Pull main branch
git pull origin main

# Verify you're on the right version
git log -1 --oneline
```

### Step 6: Update Dependencies
```bash
# Install/update Python packages
pip install -r requirements.txt --upgrade

# Or if using uv (faster)
uv pip install -r requirements.txt
```

### Step 7: Update Environment Variables
```bash
# Edit .env file to add new required variables
nano .env

# Add these new variables for Events system:
# SKIDDLE_API_KEY=your_skiddle_key
# ADMIN_API_KEY=viaduct-echo-admin-2025
# GITHUB_TOKEN=ghp_your_github_token
# GITHUB_REPO=dalebar/viaductecho
# GITHUB_BRANCH=main
# STOCKPORT_LAT=53.4106
# STOCKPORT_LON=-2.1575
# EVENT_SEARCH_RADIUS=3

# Save and exit (Ctrl+X, Y, Enter)
```

### Step 8: Run Database Migrations
```bash
# Run the events table migration
python -c "from src.database.migrations import run_migrations; run_migrations()"

# Or manually verify tables exist
python -c "from src.database.event_operations import EventOperations; db = EventOperations(); print('Events tables ready'); db.close()"
```

### Step 9: Create Required Directories
```bash
# Create directories for uploaded images and static data
mkdir -p static/event_images
mkdir -p static_data
mkdir -p logs/api

# Set proper permissions
chmod 755 static/event_images
chmod 755 static_data
```

### Step 10: Restart Services
```bash
# Start API server in background
nohup python -m src.api.app > logs/api.log 2>&1 &

# Optional: Start aggregator if you want scheduled runs
# nohup python -m src.main > logs/aggregator.log 2>&1 &

# Verify processes are running
ps aux | grep "python -m src"

# Check logs for any errors
tail -f logs/api.log
# Press Ctrl+C to stop watching logs
```

### Step 11: Verify Deployment
```bash
# Test API health endpoint
curl http://localhost:8000/health

# Test admin dashboard
curl http://localhost:8000/admin

# Check if API is responding
curl http://localhost:8000/

# Test events endpoint
curl http://localhost:8000/api/v1/events
```

### Step 12: Test from Outside EC2
From your local machine:
```bash
# Test public API
curl https://api.viaductecho.info/health

# Visit admin dashboard in browser
open https://api.viaductecho.info/admin
```

## Rollback Procedure (If Something Goes Wrong)

```bash
# Stop current processes
pkill -f "python -m src"

# Revert to previous version
git reset --hard backup-YYYYMMDD-HHMMSS
# or
git checkout <previous-commit-hash>

# Reinstall old dependencies
pip install -r requirements.txt

# Restart services
nohup python -m src.api.app > logs/api.log 2>&1 &

# Verify rollback worked
curl http://localhost:8000/health
```

## Better Production Setup (Recommended for Future)

### Option 1: Using systemd (Most Robust)

Create `/etc/systemd/system/viaduct-api.service`:
```ini
[Unit]
Description=Viaduct Echo API
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/viaductecho-backend
Environment="PATH=/home/ubuntu/.local/bin:/usr/local/bin:/usr/bin"
ExecStart=/usr/bin/python3 -m uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Then manage with:
```bash
# Enable service to start on boot
sudo systemctl enable viaduct-api

# Start/stop/restart service
sudo systemctl start viaduct-api
sudo systemctl stop viaduct-api
sudo systemctl restart viaduct-api

# View logs
sudo journalctl -u viaduct-api -f

# Check status
sudo systemctl status viaduct-api
```

**Deployment with systemd:**
```bash
cd viaductecho-backend
git pull origin main
pip install -r requirements.txt --upgrade
sudo systemctl restart viaduct-api
sudo systemctl status viaduct-api
```

### Option 2: Using PM2 (Node.js process manager, but works for Python)

```bash
# Install PM2
sudo npm install -g pm2

# Start API with PM2
pm2 start "python -m src.api.app" --name viaduct-api

# Save PM2 config
pm2 save

# Enable PM2 to start on boot
pm2 startup

# Management commands
pm2 list
pm2 logs viaduct-api
pm2 restart viaduct-api
pm2 stop viaduct-api
```

**Deployment with PM2:**
```bash
cd viaductecho-backend
git pull origin main
pip install -r requirements.txt --upgrade
pm2 restart viaduct-api
pm2 logs viaduct-api
```

## Monitoring

### Check Process Status
```bash
# See if processes are running
ps aux | grep python

# Check memory usage
free -h

# Check disk space
df -h

# Check API logs
tail -n 100 logs/api.log
```

### Check API Metrics
```bash
# Response time test
time curl http://localhost:8000/health

# View active connections (if using nginx)
sudo systemctl status nginx
```

## Environment Variables Checklist

Ensure these are in your `.env` file:

**Required:**
- ✅ `DATABASE_URL` - PostgreSQL connection (Neon)
- ✅ `ADMIN_API_KEY` - Admin dashboard auth

**Events System (NEW):**
- ✅ `SKIDDLE_API_KEY` - Events data source
- ✅ `STOCKPORT_LAT` - 53.4106
- ✅ `STOCKPORT_LON` - -2.1575
- ✅ `EVENT_SEARCH_RADIUS` - 3

**GitHub Publishing (NEW):**
- ✅ `GITHUB_TOKEN` - Personal access token
- ✅ `GITHUB_REPO` - dalebar/viaductecho
- ✅ `GITHUB_BRANCH` - main

**Optional:**
- ⚪ `OPENAI_API_KEY` - AI summaries
- ⚪ `HTTP_TIMEOUT` - Request timeout

## Troubleshooting

### Problem: Port 8000 already in use
```bash
# Find what's using the port
sudo lsof -i :8000

# Kill the process
kill <PID>
```

### Problem: Permission denied on static directories
```bash
chmod -R 755 static/event_images
chmod -R 755 static_data
chown -R $USER:$USER static/
```

### Problem: Module not found errors
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Problem: Database connection fails
```bash
# Check DATABASE_URL is correct
echo $DATABASE_URL

# Test connection
python -c "from src.database.operations import DatabaseOperations; db = DatabaseOperations(); print('Connected'); db.close()"
```

### Problem: GitHub publishing fails
```bash
# Verify GitHub token has correct permissions
# Token needs 'repo' scope

# Test token
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user

# Check repo exists and is accessible
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/repos/dalebar/viaductecho
```

## Quick Deployment Script

Save this as `deploy.sh` for one-command deployments:

```bash
#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Stop services
echo "⏹️  Stopping services..."
pkill -f "python -m src" || true

# Backup current version
echo "💾 Creating backup..."
git tag "backup-$(date +%Y%m%d-%H%M%S)"

# Pull latest code
echo "📥 Pulling latest code..."
git pull origin main

# Update dependencies
echo "📦 Updating dependencies..."
pip install -r requirements.txt --upgrade

# Run migrations
echo "🗄️  Running migrations..."
python -c "from src.database.migrations import run_migrations; run_migrations()" || true

# Create directories
echo "📁 Creating directories..."
mkdir -p static/event_images static_data logs/api

# Start services
echo "▶️  Starting services..."
nohup python -m src.api.app > logs/api.log 2>&1 &

sleep 3

# Verify
echo "✅ Verifying deployment..."
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Deployment successful!"
    echo "📊 API Status:"
    ps aux | grep "python -m src" | grep -v grep
else
    echo "❌ Deployment failed - check logs/api.log"
    exit 1
fi
```

Make it executable:
```bash
chmod +x deploy.sh
```

Then deploy with:
```bash
./deploy.sh
```
