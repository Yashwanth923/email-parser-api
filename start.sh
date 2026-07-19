#!/bin/sh
# =============================================================
# start.sh - Start email-parser-api with Ngrok tunnel
# Usage: ./start.sh
# Requires: NGROK_AUTHTOKEN set in .env file or environment
# =============================================================

set -e

# Load .env file if it exists
if [ -f ".env" ]; then
  echo "Loading environment from .env file..."
  export $(grep -v '^#' .env | xargs)
fi

# Check NGROK_AUTHTOKEN is set
if [ -z "$NGROK_AUTHTOKEN" ]; then
  echo ""
  echo "ERROR: NGROK_AUTHTOKEN is not set!"
  echo ""
  echo "Please do ONE of the following:"
  echo "  1. Create a .env file with: NGROK_AUTHTOKEN=your_token_here"
  echo "  2. Or export it: export NGROK_AUTHTOKEN=your_token_here"
  echo ""
  echo "Get your free Ngrok token at: https://dashboard.ngrok.com/get-started/your-authtoken"
  echo ""
  exit 1
fi

echo ""
echo "=============================================="
echo "  Starting Email Parser API + Ngrok Tunnel"
echo "=============================================="
echo ""

# Stop any existing containers cleanly
echo "[1/4] Stopping any existing containers..."
docker compose -f docker-compose.ngrok.yml down --remove-orphans 2>/dev/null || true

# Build the latest image
echo "[2/4] Building email-parser-api image..."
docker compose -f docker-compose.ngrok.yml build

# Start all services in background
echo "[3/4] Starting services (API + Ngrok)..."
docker compose -f docker-compose.ngrok.yml up -d

# Wait for Ngrok to be ready and fetch public URL
echo "[4/4] Waiting for Ngrok tunnel to be ready..."
echo ""

MAX_WAIT=60
WAITED=0
NGROK_URL=""

while [ $WAITED -lt $MAX_WAIT ]; do
  # Query Ngrok local API for tunnel info
  NGROK_URL=$(curl -s http://localhost:4040/api/tunnels 2>/dev/null \
    | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tunnels = data.get('tunnels', [])
    for t in tunnels:
        url = t.get('public_url', '')
        if url.startswith('https://'):
            print(url)
            break
except:
    pass
" 2>/dev/null)

  if [ -n "$NGROK_URL" ]; then
    break
  fi

  sleep 2
  WAITED=$((WAITED + 2))
  printf "."
done

echo ""
echo ""

if [ -n "$NGROK_URL" ]; then
  echo "=============================================="
  echo "  SUCCESS! Your services are running."
  echo "=============================================="
  echo ""
  echo "  Local API URL    : http://localhost:8000"
  echo "  Ngrok Public URL : $NGROK_URL"
  echo "  Ngrok Dashboard  : http://localhost:4040"
  echo ""
  echo "  Share this URL with your devs:"
  echo "  --> $NGROK_URL"
  echo ""
  echo "  API Docs available at:"
  echo "  --> $NGROK_URL/docs"
  echo "  --> $NGROK_URL/redoc"
  echo ""
  echo "=============================================="
  echo ""
  echo "  To stop all services run:"
  echo "  docker compose -f docker-compose.ngrok.yml down"
  echo ""
else
  echo "=============================================="
  echo "  WARNING: Could not retrieve Ngrok URL."
  echo "=============================================="
  echo ""
  echo "  Services may still be starting up."
  echo "  Please check Ngrok dashboard at: http://localhost:4040"
  echo "  Or check logs with:"
  echo "  docker logs email-parser-ngrok"
  echo ""
  echo "  To stop all services run:"
  echo "  docker compose -f docker-compose.ngrok.yml down"
  echo ""
fi