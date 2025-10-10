"""
GraphRAG POC Helper Functions
Simple utilities for TMDB data fetching, Neo4j graph building, and RAG implementations
"""

import os
import time
import requests
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from neo4j import GraphDatabase
from sentence_transformers import SentenceTransformer
from openai import OpenAI
import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Fix HuggingFace tokenizers warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

class TMDBClient:
    """Simple TMDB API client for fetching movie data"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.themoviedb.org/3"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        # Also add API key as query parameter for some endpoints
        self.params = {"api_key": api_key}
    
    def get_popular_people(self, limit: int = 20) -> List[Dict]:
        """Fetch popular Tamil cinema actors/directors"""
        # Known Tamil cinema actors/directors
        tamil_actors = [
            "Rajinikanth", "Kamal Haasan", "Vijay", "Ajith Kumar", "Dhanush",
            "Surya", "Vikram", "Karthi", "Simbu", "Arya", "Jeeva", "Madhavan",
            "Sivakarthikeyan", "Vishal", "Jiiva", "Bharath", "Siddharth",
            "Manoj Bajpayee", "Prakash Raj", "Nassar", "Vadivelu", "Vivek"
        ]
        
        all_people = []
        
        # Search for each Tamil actor
        for actor_name in tamil_actors[:limit]:
            try:
                url = f"{self.base_url}/search/person"
                params = {
                    "query": actor_name,
                    "page": 1,
                    "include_adult": False,
                    "api_key": self.api_key
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                if data["results"]:
                    # Take the first result (most likely match)
                    person = data["results"][0]
                    if person.get("known_for_department") in ["Acting", "Directing"]:
                        all_people.append(person)
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error searching for {actor_name}: {e}")
                continue
        
        return all_people[:limit]
    
    def get_person_details(self, person_id: int) -> Dict:
        """Get detailed information about a person"""
        url = f"{self.base_url}/person/{person_id}"
        params = {"append_to_response": "movie_credits", "api_key": self.api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def get_movie_details(self, movie_id: int) -> Dict:
        """Get detailed information about a movie"""
        url = f"{self.base_url}/movie/{movie_id}"
        params = {"append_to_response": "credits,keywords", "api_key": self.api_key}
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        return response.json()
    
    def fetch_artists_and_movies(self, num_artists: int = 15) -> pd.DataFrame:
        """Fetch Tamil cinema actors and their top movies"""
        print(f"Fetching {num_artists} popular Tamil cinema actors and their movies...")
        
        # Get popular Tamil people
        people = self.get_popular_people(num_artists)
        
        all_data = []
        
        for person in people:
            try:
                # Get person details with movie credits
                person_details = self.get_person_details(person["id"])
                
                # Get top 3-5 movies for this person
                movie_credits = person_details.get("movie_credits", {})
                movies = movie_credits.get("cast", [])[:5]  # Top 5 movies
                
                for movie in movies:
                    try:
                        # Get detailed movie information
                        movie_details = self.get_movie_details(movie["id"])
                        
                        # Filter for Tamil movies (check original language or production countries)
                        original_language = movie_details.get("original_language", "")
                        production_countries = [country.get("iso_3166_1", "") for country in movie_details.get("production_countries", [])]
                        
                        # Skip if not Tamil movie (ta = Tamil language code, IN = India)
                        if original_language != "ta" and "IN" not in production_countries:
                            continue
                        
                        # Extract relevant data
                        movie_data = {
                            "person_id": person["id"],
                            "person_name": person["name"],
                            "person_known_for": person.get("known_for_department", "Acting"),
                            "movie_id": movie["id"],
                            "movie_title": movie["title"],
                            "movie_overview": movie.get("overview", ""),
                            "movie_release_date": movie.get("release_date", ""),
                            "movie_vote_average": movie.get("vote_average", 0),
                            "movie_vote_count": movie.get("vote_count", 0),
                            "movie_genres": [g["name"] for g in movie_details.get("genres", [])],
                            "movie_directors": [d["name"] for d in movie_details.get("credits", {}).get("crew", []) 
                                             if d.get("job") == "Director"],
                            "movie_cast": [c["name"] for c in movie_details.get("credits", {}).get("cast", [])[:5]],
                            "original_language": original_language
                        }
                        
                        all_data.append(movie_data)
                        
                    except Exception as e:
                        print(f"Error fetching movie {movie['id']}: {e}")
                        continue
                
                # Small delay to respect rate limits
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error fetching person {person['id']}: {e}")
                continue
        
        return pd.DataFrame(all_data)


class Neo4jGraphBuilder:
    """Build knowledge graph in Neo4j from TMDB data"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
    
    def close(self):
        self.driver.close()
    
    def clear_database(self):
        """Clear all nodes and relationships"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
    
    def build_graph(self, df: pd.DataFrame):
        """Build knowledge graph from DataFrame"""
        print("Building knowledge graph in Neo4j...")
        
        with self.driver.session() as session:
            # Create constraints
            session.run("CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE")
            session.run("CREATE CONSTRAINT movie_id IF NOT EXISTS FOR (m:Movie) REQUIRE m.id IS UNIQUE")
            session.run("CREATE CONSTRAINT genre_name IF NOT EXISTS FOR (g:Genre) REQUIRE g.name IS UNIQUE")
            
            # Create nodes and relationships
            for _, row in df.iterrows():
                # Create Person node
                session.run("""
                    MERGE (p:Person {id: $person_id})
                    SET p.name = $person_name, p.known_for = $person_known_for
                """, person_id=row["person_id"], person_name=row["person_name"], 
                       person_known_for=row["person_known_for"])
                
                # Create Movie node
                session.run("""
                    MERGE (m:Movie {id: $movie_id})
                    SET m.title = $movie_title, m.overview = $movie_overview,
                        m.release_date = $movie_release_date, m.vote_average = $movie_vote_average,
                        m.vote_count = $movie_vote_count
                """, movie_id=row["movie_id"], movie_title=row["movie_title"],
                       movie_overview=row["movie_overview"], movie_release_date=row["movie_release_date"],
                       movie_vote_average=row["movie_vote_average"], movie_vote_count=row["movie_vote_count"])
                
                # Create ACTED_IN relationship
                session.run("""
                    MERGE (p:Person {id: $person_id})
                    MERGE (m:Movie {id: $movie_id})
                    MERGE (p)-[:ACTED_IN]->(m)
                """, person_id=row["person_id"], movie_id=row["movie_id"])
                
                # Create Genre nodes and relationships
                for genre in row["movie_genres"]:
                    session.run("""
                        MERGE (g:Genre {name: $genre_name})
                        MERGE (m:Movie {id: $movie_id})
                        MERGE (m)-[:HAS_GENRE]->(g)
                    """, genre_name=genre, movie_id=row["movie_id"])
                
                # Create Director nodes and relationships
                for director in row["movie_directors"]:
                    session.run("""
                        MERGE (d:Person {name: $director_name})
                        SET d.known_for = 'Directing'
                        MERGE (m:Movie {id: $movie_id})
                        MERGE (d)-[:DIRECTED]->(m)
                    """, director_name=director, movie_id=row["movie_id"])
        
        print("Knowledge graph built successfully!")
    
    def get_graph_stats(self) -> Dict:
        """Get statistics about the graph"""
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
            for record in result:
                label = record["label"][0] if record["label"] else "Unknown"
                stats[f"{label}_count"] = record["count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count")
            for record in result:
                stats[f"{record['rel_type']}_count"] = record["count"]
            
            return stats


class SimpleRAG:
    """Simple RAG implementation using vector embeddings"""
    
    def __init__(self, openai_api_key: str):
        self.client = OpenAI(api_key=openai_api_key)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.documents = []
        self.embeddings = None
    
    def add_documents(self, df: pd.DataFrame):
        """Add movie documents to the vector store"""
        print("Building vector embeddings for RAG...")
        
        for _, row in df.iterrows():
            # Create text representation of movie
            doc_text = f"""
            Movie: {row['movie_title']}
            Overview: {row['movie_overview']}
            Genres: {', '.join(row['movie_genres'])}
            Cast: {', '.join(row['movie_cast'])}
            Directors: {', '.join(row['movie_directors'])}
            Release Date: {row['movie_release_date']}
            Rating: {row['movie_vote_average']}
            """
            
            self.documents.append({
                'text': doc_text,
                'movie_id': row['movie_id'],
                'movie_title': row['movie_title'],
                'metadata': row.to_dict()
            })
        
        # Create embeddings
        texts = [doc['text'] for doc in self.documents]
        self.embeddings = self.embedding_model.encode(texts)
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search for similar documents"""
        query_embedding = self.embedding_model.encode([query])
        
        # Calculate similarities
        similarities = np.dot(self.embeddings, query_embedding.T).flatten()
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            results.append({
                'document': self.documents[idx],
                'similarity': float(similarities[idx])
            })
        
        return results
    
    def generate_recommendations(self, query: str, top_k: int = 5) -> str:
        """Generate recommendations using RAG"""
        # Search for relevant documents
        search_results = self.search(query, top_k)
        
        # Debug: Show what movies are being considered
        print(f"🔍 RAG found {len(search_results)} relevant movies:")
        for i, result in enumerate(search_results, 1):
            print(f"  {i}. {result['document']['movie_title']} (similarity: {result['similarity']:.3f})")
        
        # Prepare context
        context = "\n\n".join([
            f"Movie: {result['document']['movie_title']}\n{result['document']['text']}"
            for result in search_results
        ])
        
        # Generate response using OpenAI
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert. You MUST ONLY recommend movies from the provided context. Do not recommend any movies that are not in the context. Base your recommendations strictly on the provided movie information."},
                {"role": "user", "content": f"Query: {query}\n\nContext (ONLY recommend from these movies):\n{context}\n\nPlease provide your top {top_k} movie recommendations from the context above with detailed reasoning. Do not recommend any movies not listed in the context."}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content


class GraphRAG:
    """GraphRAG implementation using Neo4j graph traversal"""
    
    def __init__(self, neo4j_uri: str, neo4j_user: str, neo4j_password: str, openai_api_key: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
        self.client = OpenAI(api_key=openai_api_key)
    
    def close(self):
        self.driver.close()
    
    def extract_subgraph_context(self, query: str) -> str:
        """Extract relevant subgraph context based on query"""
        with self.driver.session() as session:
            # Simple keyword-based graph traversal
            # Look for movies with matching genres or actors
            query_lower = query.lower()
            
            if "action" in query_lower:
                genre_filter = "g.name = 'Action'"
            elif "comedy" in query_lower:
                genre_filter = "g.name = 'Comedy'"
            elif "drama" in query_lower:
                genre_filter = "g.name = 'Drama'"
            else:
                genre_filter = "true"  # No genre filter
            
            # Get movies with their relationships
            cypher_query = f"""
            MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
            WHERE {genre_filter}
            WITH m, collect(g.name) as genres
            MATCH (m)<-[:ACTED_IN]-(p:Person)
            WITH m, genres, collect(p.name) as actors
            MATCH (m)<-[:DIRECTED]-(d:Person)
            WITH m, genres, actors, collect(d.name) as directors
            RETURN m.title as title, m.overview as overview, m.vote_average as rating,
                   genres, actors, directors
            ORDER BY m.vote_average DESC
            LIMIT 10
            """
            
            result = session.run(cypher_query)
            
            context_parts = []
            for record in result:
                context_parts.append(f"""
                Movie: {record['title']}
                Overview: {record['overview']}
                Genres: {', '.join(record['genres'])}
                Actors: {', '.join(record['actors'][:3])}
                Directors: {', '.join(record['directors'])}
                Rating: {record['rating']}
                """)
            
            return "\n".join(context_parts)
    
    def generate_recommendations(self, query: str) -> str:
        """Generate recommendations using GraphRAG"""
        # Extract graph context
        graph_context = self.extract_subgraph_context(query)
        
        # Debug: Show what movies are being considered
        print(f"🕸️ GraphRAG found movies in context:")
        lines = graph_context.split('\n')
        movie_titles = [line for line in lines if line.startswith('Movie:')]
        for i, title in enumerate(movie_titles[:5], 1):
            print(f"  {i}. {title.replace('Movie: ', '')}")
        
        # Generate response using OpenAI with graph context
        response = self.client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a movie recommendation expert. You MUST ONLY recommend movies from the provided graph context. Do not recommend any movies that are not in the context. Use the graph relationships and connections between movies, actors, directors, and genres to provide intelligent recommendations based ONLY on the provided data."},
                {"role": "user", "content": f"Query: {query}\n\nGraph Context (ONLY recommend from these movies):\n{graph_context}\n\nPlease provide your top 5 movie recommendations from the context above with detailed reasoning based on the graph relationships. Do not recommend any movies not listed in the context."}
            ],
            max_tokens=500,
            temperature=0.7
        )
        
        return response.choices[0].message.content


def visualize_graph_sample(neo4j_uri: str, neo4j_user: str, neo4j_password: str, limit: int = 20):
    """Visualize a sample of the knowledge graph"""
    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))
    
    with driver.session() as session:
        # Get a sample of the graph
        result = session.run(f"""
            MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
            WITH m, collect(g.name) as genres
            MATCH (m)<-[:ACTED_IN]-(p:Person)
            WITH m, genres, collect(p.name)[0..2] as actors
            RETURN m.title as movie, genres, actors
            LIMIT {limit}
        """)
        
        # Create NetworkX graph
        G = nx.Graph()
        
        for record in result:
            movie = record['movie']
            G.add_node(movie, type='movie')
            
            for genre in record['genres']:
                G.add_node(genre, type='genre')
                G.add_edge(movie, genre)
            
            for actor in record['actors']:
                G.add_node(actor, type='actor')
                G.add_edge(movie, actor)
        
        # Visualize
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, k=1, iterations=50)
        
        # Color nodes by type
        node_colors = []
        for node in G.nodes():
            if G.nodes[node].get('type') == 'movie':
                node_colors.append('lightblue')
            elif G.nodes[node].get('type') == 'genre':
                node_colors.append('lightgreen')
            else:  # actor
                node_colors.append('lightcoral')
        
        nx.draw(G, pos, node_color=node_colors, with_labels=True, 
                node_size=1000, font_size=8, font_weight='bold')
        
        plt.title("Knowledge Graph Sample (Movies, Genres, Actors)")
        plt.show()
    
    driver.close()


def compare_rag_vs_graphrag(query: str, df: pd.DataFrame, neo4j_uri: str, 
                           neo4j_user: str, neo4j_password: str, openai_api_key: str):
    """Compare RAG vs GraphRAG recommendations"""
    
    print("=" * 60)
    print("RAG vs GraphRAG Comparison")
    print("=" * 60)
    print(f"Query: {query}\n")
    
    # Initialize RAG
    rag = SimpleRAG(openai_api_key)
    rag.add_documents(df)
    
    # Initialize GraphRAG
    graphrag = GraphRAG(neo4j_uri, neo4j_user, neo4j_password, openai_api_key)
    
    # Get recommendations
    print("🔍 Regular RAG Recommendations:")
    print("-" * 40)
    rag_recommendations = rag.generate_recommendations(query)
    print(rag_recommendations)
    
    print("\n🕸️ GraphRAG Recommendations:")
    print("-" * 40)
    graphrag_recommendations = graphrag.generate_recommendations(query)
    print(graphrag_recommendations)
    
    # Cleanup
    graphrag.close()
    
    return {
        'rag': rag_recommendations,
        'graphrag': graphrag_recommendations
    }
