#!/usr/bin/env bash
set -e
echo "Setting up SentinelEdge Environment..."
python3 -m venv backend/.venv
python3 -m venv edge/.venv

./backend/.venv/bin/pip install -e "./backend[dev]"
./edge/.venv/bin/pip install -e "./edge"

cd frontend && npm install && cd ..
cp .env.example .env
echo "Setup complete!"
