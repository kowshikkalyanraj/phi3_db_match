#!/bin/bash
# start.sh - optimized startup for Phi-3 Mini pipeline

export OLLAMA_KEEP_ALIVE=5m

# Ensure Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Ollama is not running. Starting Ollama..."
    brew services start ollama 2>/dev/null || ollama serve &
    sleep 3
fi

# Activate virtual environment if present
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo "🔥 Pre-warming Phi-3 Mini..."
python optimize_for_speed.py

echo "🚀 Running pipeline..."
python main.py --batch
