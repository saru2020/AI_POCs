# 🎬 Movies GraphRAG POC

A dead simple POC demonstrating GraphRAG vs regular RAG for movie recommendations using a Jupyter notebook. Perfect for understanding the core concepts and differences between the two approaches.

## 🎯 What This POC Demonstrates

- **Data Collection**: Fetches 15 popular artists and their movies from TMDB API
- **Knowledge Graph**: Builds a Neo4j graph with movies, actors, directors, and genres
- **Regular RAG**: Uses vector embeddings for similarity search
- **GraphRAG**: Uses graph traversal and relationships for recommendations
- **Side-by-Side Comparison**: Shows the differences between both approaches

## 🚀 Quick Start (Jupyter Demo)

### Option 1: Automated Setup
```bash
# 1. Set up environment
cp env.example .env
# Add your TMDB_API_KEY and OPENAI_API_KEY to .env

# 2. Run the demo (automatically starts Neo4j, installs deps, launches Jupyter)
./run_demo.sh
```

### Option 2: Manual Setup
```bash
# 1. Start Neo4j
docker compose up neo4j

# 2. Set up environment
cp env.example .env
# Add your TMDB_API_KEY and OPENAI_API_KEY to .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the demo
jupyter notebook demo_graphrag.ipynb
```

## 🔑 Required API Keys

Get your API keys and add them to `.env`:

- **TMDB API**: https://www.themoviedb.org/settings/api
- **OpenAI API**: https://platform.openai.com/api-keys

## 📊 Key Differences: RAG vs GraphRAG

| Aspect | Regular RAG | GraphRAG |
|--------|-------------|----------|
| **Data Structure** | Flat text documents | Graph with relationships |
| **Search Method** | Vector similarity | Graph traversal |
| **Context** | Text-based | Relationship-based |
| **Reasoning** | Surface-level similarity | Deep relationship analysis |
| **Scalability** | Good for large text | Better for complex relationships |

## 🏗️ Architecture

```
TMDB API → Data Collection → Neo4j Graph → GraphRAG
    ↓                           ↓
Vector Store → Regular RAG → Comparison
```

## 🛠️ Tech Stack

- **Jupyter Notebook**: Interactive demo environment
- **Neo4j**: Graph database for relationships
- **OpenAI API**: LLM for recommendations
- **TMDB API**: Movie data source
- **Python Libraries**: pandas, networkx, matplotlib, seaborn

## 📋 What You'll See

1. **Data Collection**: Real movie data from TMDB
2. **Graph Visualization**: Interactive knowledge graph
3. **RAG Implementation**: Vector-based similarity search
4. **GraphRAG Implementation**: Relationship-based reasoning
5. **Comparison**: Side-by-side analysis of both approaches
6. **Insights**: Analysis of the differences and benefits

## 🎯 Success Criteria

- ✅ Notebook runs end-to-end in < 5 minutes
- ✅ Clear visual demonstration of GraphRAG vs RAG difference
- ✅ Knowledge graph visualization showing relationships
- ✅ Working example with 15 artists and their movies
- ✅ Side-by-side comparison of both approaches

## 📚 Understanding GraphRAG

### Regular RAG
- Treats movies as flat text documents
- Uses vector embeddings for similarity search
- Finds movies based on text similarity

### GraphRAG
- Leverages relationships between movies, actors, directors, genres
- Uses graph traversal to find connected movies
- Provides contextual reasoning about why movies are similar

## 🔧 Local Services

- **Neo4j Browser**: http://localhost:7474 (neo4j/movies123)
- **Jupyter Notebook**: http://localhost:8888 (when running)

## 📝 Example Queries

The notebook demonstrates these sample queries:
- "Recommend action movies with great actors"
- "I want comedy movies with good ratings"
- "Show me drama movies from talented directors"

## 🎓 Learning Outcomes

After running this POC, you'll understand:
- How to build a knowledge graph from real data
- The difference between vector similarity and graph traversal
- When to use RAG vs GraphRAG
- How to implement both approaches
- The benefits of relationship-based reasoning

## 🚀 Next Steps

- Add more complex graph queries
- Implement multi-hop reasoning
- Scale to larger datasets
- Add user preferences and feedback
- Build a production system

## 📄 License

This project is licensed under the MIT License.

---

**Perfect for demos, learning, and understanding GraphRAG concepts!**