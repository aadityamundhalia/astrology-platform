#!/bin/bash
# Wait for Ollama to be ready
until curl -s http://localhost:11434/api/tags > /dev/null; do
  echo "Waiting for Ollama..."
  sleep 2
done

echo "Pulling models..."
ollama pull granite4:latest
ollama pull nomic-embed-text

echo "Models ready!"
# Keep the container running
tail -f /dev/null