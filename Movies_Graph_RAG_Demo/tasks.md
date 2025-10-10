# Movies GraphRAG POC - Simplified Tasks

## 🎯 Project Overview
A dead simple POC to demonstrate GraphRAG vs regular RAG using a Jupyter notebook. Fetches 15 artists and their movies from TMDB, builds a knowledge graph, and compares both approaches.

## 📋 Core Tasks

### 1. Setup & Dependencies ✅
- [x] Create minimal `requirements.txt` with essential packages
- [x] Create `env.example` with required API keys
- [x] Update `docker-compose.yml` to include only Neo4j service

### 2. Helper Module ✅
- [x] Create `src/utils/graphrag_helpers.py` with:
  - `TMDBClient`: Fetch 15 artists and their movies from TMDB API
  - `Neo4jGraphBuilder`: Build knowledge graph in Neo4j
  - `SimpleRAG`: Regular RAG with vector embeddings
  - `GraphRAG`: GraphRAG with graph traversal
  - `visualize_graph_sample`: Graph visualization
  - `compare_rag_vs_graphrag`: Side-by-side comparison

### 3. Jupyter Notebook Demo ✅
- [x] Create `demo_graphrag.ipynb` with 8 sections:
  1. **Setup and Imports**
  2. **Data Collection from TMDB API**
  3. **Build Knowledge Graph in Neo4j**
  4. **Visualize the Knowledge Graph**
  5. **Regular RAG Implementation**
  6. **GraphRAG Implementation**
  7. **Side-by-Side Comparison**
  8. **Analysis and Insights**

### 4. Documentation ✅
- [x] Update `tasks.md` with simplified POC tasks
- [x] Update `README.md` with Jupyter demo instructions

## 🚀 Quick Start

```bash
# 1. Start Neo4j
docker-compose up neo4j

# 2. Set up environment
cp env.example .env
# Add your TMDB_API_KEY and OPENAI_API_KEY to .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the demo
jupyter notebook demo_graphrag.ipynb
```

## 🎯 Success Criteria
- [x] Notebook runs end-to-end in < 5 minutes
- [x] Clear visual demonstration of GraphRAG vs RAG difference
- [x] Knowledge graph visualization showing relationships
- [x] Working example with 15 artists and their movies
- [x] Side-by-side comparison of both approaches

## 📊 What the POC Demonstrates

### Regular RAG
- Uses vector embeddings for similarity search
- Treats movies as flat text documents
- Finds movies based on text similarity

### GraphRAG
- Uses Neo4j graph traversal
- Leverages relationships between movies, actors, directors, genres
- Provides contextual reasoning about why movies are similar

### Key Differences
| Aspect | Regular RAG | GraphRAG |
|--------|-------------|----------|
| Data Structure | Flat text | Graph with relationships |
| Search Method | Vector similarity | Graph traversal |
| Context | Text-based | Relationship-based |
| Reasoning | Surface-level | Deep relationship analysis |

## 📝 Notes
- This is a minimal POC focused on demonstrating the core concepts
- Uses real TMDB data for authenticity
- Designed to run locally with minimal setup
- Perfect for demos and learning GraphRAG concepts