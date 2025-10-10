#!/bin/bash

# GraphRAG POC Demo Runner
echo "🎬 Starting GraphRAG POC Demo..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "📋 Please copy env.example to .env and add your API keys:"
    echo "   cp env.example .env"
    echo "   # Then edit .env and add your TMDB_API_KEY and OPENAI_API_KEY"
    exit 1
fi

# Check if API keys are set
if ! grep -q "TMDB_API_KEY=your_tmdb_api_key_here" .env; then
    echo "✅ TMDB_API_KEY found in .env"
else
    echo "❌ Please set your TMDB_API_KEY in .env file"
    exit 1
fi

if ! grep -q "OPENAI_API_KEY=your_openai_api_key_here" .env; then
    echo "✅ OPENAI_API_KEY found in .env"
else
    echo "❌ Please set your OPENAI_API_KEY in .env file"
    exit 1
fi

# Start Neo4j
echo "🚀 Starting Neo4j..."
docker compose up neo4j -d

# Wait for Neo4j to be ready
echo "⏳ Waiting for Neo4j to be ready..."
sleep 10

# Check if Neo4j is accessible
if curl -s http://localhost:7474 > /dev/null; then
    echo "✅ Neo4j is ready!"
else
    echo "❌ Neo4j is not accessible. Please check the logs:"
    echo "   docker compose logs neo4j"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -r requirements.txt

# Start Jupyter notebook
echo "🎯 Starting Jupyter notebook..."
echo "📖 Open your browser to the URL shown below"
echo "📝 Run the demo_graphrag.ipynb notebook"
echo ""
jupyter notebook demo_graphrag.ipynb
