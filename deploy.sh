#!/bin/bash

# Viaduct Echo Deployment Script
# Pulls latest code and restarts API and scheduler

set -e  # Exit on any error

echo "=================================="
echo "Viaduct Echo Deployment"
echo "=================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Ensure required directories exist
mkdir -p logs
mkdir -p static/event_images
chmod 755 static/event_images
echo -e "${GREEN}✓ Directories created${NC}"
echo "  - logs/"
echo "  - static/event_images/"
echo ""

echo "Step 1: Pulling latest code from GitHub..."
git pull origin main
echo -e "${GREEN}✓ Code updated${NC}"
echo ""

echo "Step 2: Stopping existing processes..."
# Stop API
API_PID=$(pgrep -f "python -m src.api.app" || true)
if [ -n "$API_PID" ]; then
    pkill -f "python -m src.api.app"
    echo -e "${YELLOW}  Stopped API (PID: $API_PID)${NC}"
else
    echo "  API was not running"
fi

# Stop scheduler
SCHEDULER_PID=$(pgrep -f "python -m src.main" || true)
if [ -n "$SCHEDULER_PID" ]; then
    pkill -f "python -m src.main"
    echo -e "${YELLOW}  Stopped scheduler (PID: $SCHEDULER_PID)${NC}"
else
    echo "  Scheduler was not running"
fi

# Wait for processes to stop
sleep 2
echo -e "${GREEN}✓ Processes stopped${NC}"
echo ""

echo "Step 3: Starting API..."
nohup python -m src.api.app > logs/api.log 2>&1 &
sleep 1

# Verify API started
API_PID=$(pgrep -f "python -m src.api.app" || true)
if [ -n "$API_PID" ]; then
    echo -e "${GREEN}✓ API started (PID: $API_PID)${NC}"
else
    echo -e "${RED}✗ Failed to start API${NC}"
    exit 1
fi
echo ""

echo "Step 4: News Scheduler"
echo "The news scheduler runs automatically every hour (5 AM - 8 PM)."
echo "You can now trigger it manually from the admin dashboard."
echo ""
echo -n "Do you want to start the automatic scheduler? (y/N): "
read -r response

if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "Starting scheduler..."

    # Check if scheduler is set up for production in main.py
    if grep -q "# echo.start_scheduler()" src/main.py; then
        echo -e "${YELLOW}⚠ Warning: Scheduler is commented out in src/main.py${NC}"
        echo "To enable automatic scheduling, uncomment line 125 in src/main.py:"
        echo "  echo.start_scheduler()  # Uncomment this"
        echo "and comment out line 122:"
        echo "  # echo.run_once()  # Comment this out"
        echo ""
        echo "Skipping scheduler start..."
    else
        nohup python -m src.main > logs/scheduler.log 2>&1 &
        sleep 1

        SCHEDULER_PID=$(pgrep -f "python -m src.main" || true)
        if [ -n "$SCHEDULER_PID" ]; then
            echo -e "${GREEN}✓ Scheduler started (PID: $SCHEDULER_PID)${NC}"
        else
            echo -e "${RED}✗ Failed to start scheduler${NC}"
        fi
    fi
else
    echo "Skipping scheduler start. Use the admin dashboard to run manually."
fi
echo ""

echo "=================================="
echo "Deployment Status"
echo "=================================="
echo ""

# Check API
if lsof -i :8000 > /dev/null 2>&1; then
    API_PID=$(pgrep -f "python -m src.api.app" || echo "unknown")
    echo -e "${GREEN}✓ API is running${NC} (PID: $API_PID, Port: 8000)"
else
    echo -e "${RED}✗ API is NOT running${NC}"
fi

# Check scheduler
SCHEDULER_PID=$(pgrep -f "python -m src.main" || true)
if [ -n "$SCHEDULER_PID" ]; then
    echo -e "${GREEN}✓ Scheduler is running${NC} (PID: $SCHEDULER_PID)"
else
    echo -e "${YELLOW}○ Scheduler is NOT running${NC} (use admin dashboard for manual runs)"
fi

echo ""
echo "Recent API log (last 10 lines):"
echo "---"
tail -10 logs/api.log 2>/dev/null || echo "No API logs yet"
echo ""

echo -e "${GREEN}Deployment complete!${NC}"
echo "API: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo ""
echo "To view logs:"
echo "  tail -f logs/api.log"
echo "  tail -f logs/scheduler.log"
echo ""
