#!/usr/bin/env bash
# Simple helper to run Cyber-Sensei locally without Docker.
# Usage: ./run_local.sh [backend|frontend|all]

set -e
ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

case "$1" in
  backend)
    echo "Starting backend (uvicorn)..."
    cd "$ROOT_DIR/backend"
    # Ensure PYTHONPATH includes the backend root
    export PYTHONPATH="$ROOT_DIR/backend"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ;;
  frontend)
    echo "Starting frontend (Vite)..."
    cd "$ROOT_DIR/frontend"
    npm install
    npm run dev
    ;;
  all|"")
    echo "Starting backend in the foreground. Open a new terminal to start frontend."
    cd "$ROOT_DIR/backend"
    export PYTHONPATH="$ROOT_DIR/backend"
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
    ;;
  *)
    echo "Usage: $0 [backend|frontend|all]"
    exit 1
    ;;
esac
