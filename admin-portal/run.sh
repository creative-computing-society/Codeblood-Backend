#!/bin/bash
echo "Starting Admin Backend..."
uvicorn app.main:app --host 0.0.0.0 --port 8000