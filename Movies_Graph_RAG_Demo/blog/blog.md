# My Journey Exploring RAG vs GraphRAG

## Introduction
I knew what was RAG and GraphRAG, but didn't clearly understood how only the relationships in GraphRAG were performing better than simple/plain RAGs, so I did a POC to see if it does really make sense.
There are many relationship based systems(fraud detection, social media recommendation, etc) where GraphRAG is really useful that could be picked up for the POC but I wanted something simple yet close to my passion, so I picked up the movie recommendation system which has entities/nodes like movies, actors, genres, directors, etc and relationship among them is easy to understand for everyone too.

## Tech Stack / Tools

- Neo4j for graph building logic
- TMDB API for movies data
- Open AI API for LLM integration


## Source Code:

I've made all the code available in my [GitHub repository](https://github.com/saru2020/AI_POCs/tree/main/Movies_Graph_RAG_Demo), so that you don't have to read my BS in this blog.

Just run the Jupyter notebook and explore it yourself or if you don't want to even do that, then just watch the [demo gif]((https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/demo.gif)) in the repo




## Technical Implementation

### Fetch movies data
note: I kept it intentionally small - just 15 artists and their top movies with some hardcoded popular names from Tamil Cinema.

```python
# Initialize TMDB client
tmdb_api_key = os.getenv('TMDB_API_KEY')
if not tmdb_api_key:
    print("❌ Please set TMDB_API_KEY in your .env file")
    print("Get your API key from: https://www.themoviedb.org/settings/api")
else:
    tmdb_client = TMDBClient(tmdb_api_key)
    print("✅ TMDB client initialized")
```
![1](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/1.png)


### Building the Knowledge Graph

First, I needed to create a proper knowledge graph. I used Neo4j to model the relationships:

```cypher
// My graph schema
CREATE (m:Movie {title: "The Dark Knight", rating: 9.0})
CREATE (a:Person {name: "Christian Bale", type: "Actor"})
CREATE (g:Genre {name: "Action"})
CREATE (d:Person {name: "Christopher Nolan", type: "Director"})

CREATE (a)-[:ACTED_IN]->(m)
CREATE (m)-[:HAS_GENRE]->(g)
CREATE (d)-[:DIRECTED]->(m)
```

The graph structure was simple but powerful:
- **Movies** connected to **Actors** via `ACTED_IN`
- **Movies** connected to **Directors** via `DIRECTED`  
- **Movies** connected to **Genres** via `HAS_GENRE`


### The RAG Implementation: Vector Similarity

For regular RAG, I created text embeddings from movie metadata:

```python
class SimpleRAG:
    def add_documents(self, df):
        for _, row in df.iterrows():
            doc_text = f"""
            Movie: {row['movie_title']}
            Overview: {row['movie_overview']}
            Genres: {', '.join(row['movie_genres'])}
            Cast: {', '.join(row['movie_cast'])}
            Directors: {', '.join(row['movie_directors'])}
            """
            self.documents.append({'text': doc_text, 'metadata': row.to_dict()})
        
        # Create embeddings
        self.embeddings = self.embedding_model.encode(texts)
```

This approach treats each movie as a flat text document and uses cosine similarity to find relevant matches.

### The GraphRAG Implementation: Relationship Traversal

For GraphRAG, I implemented graph traversal to extract contextual relationships:

```python
def extract_subgraph_context(self, query):
    # Query the graph based on relationships
    cypher_query = f"""
    MATCH (m:Movie)-[:HAS_GENRE]->(g:Genre)
    WHERE {genre_filter}
    WITH m, collect(g.name) as genres
    MATCH (m)<-[:ACTED_IN]-(p:Person)
    WITH m, genres, collect(p.name) as actors
    MATCH (m)<-[:DIRECTED]-(d:Person)
    WITH m, genres, actors, collect(d.name) as directors
    RETURN m.title, m.overview, genres, actors, directors
    """
```

This approach leverages the graph structure to find movies through their relationships, not just text similarity.

![2](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/2.png)


### Visualising the Graph
I created a simple graph visualization to see what was happening:

```python
def visualize_graph_sample(neo4j_uri, neo4j_user, neo4j_password, limit=20):
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
    # ... visualization code
```

![3](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/3.png)


### The First Test: Action Movies

I started with a simple query: *"Recommend action movies with great actors"*

#### Regular RAG Results:
```
1. Ra.One (similarity: 0.583)
2. Vettaiyan (similarity: 0.440)
3. Michael Madana Kama Rajan (similarity: 0.431)
```
![4](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/4.png)

The RAG system found movies that contained the words "action" and "actors" in their metadata. Pretty straightforward stuff.
We already noticed a few issues wrt results where the first 2 were actions flicks though mediocre ones but the last one MMKR wasn't much of an action flick so we know where RAG system really lacks now, it doesn't really know the context since the relationships are missing which plays a crucial part in adding extra relevant context. Now, lets see the results of GraphRAG.

#### GraphRAG Results:
```
Amaran
Ko
Sivaji: The Boss
Indian
Paiyaa
```
![5](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/5.png)
The GraphRAG system found movies through *relationships* - shared actors, directors, and genre connections. The reasoning was more contextual.

We could already see that the GraphRAG worked really well by picking exactly only the action movies and that too the great ones which showcases adding more context through relationships does help LLMs in picking more right choices.

### The Comedy Test: A Surprising Success

Next, I tried: *"I want comedy movies with good ratings"*

![6](https://raw.githubusercontent.com/saru2020/AI_POCs/main/Movies_Graph_RAG_Demo/blog/screenshots/6.png)

#### Regular RAG Results:
```
🔍 RAG found 5 relevant movies:
  1. Kaithi 2 (similarity: 0.331)
  2. Madurey (similarity: 0.331)
  3. Nitham Oru Vaanam (similarity: 0.326)
  4. Villu (similarity: 0.325)
  5. Uppu (similarity: 0.310)
Based on the provided context of movies, here are the top 5 comedy movie recommendations with good ratings:

1. **Nitham Oru Vaanam**
   - **Rating:** 6.6
   - **Overview:** This movie blends romance, thriller, and comedy genres, making it an entertaining watch for those looking for a mix of emotions. The storyline follows an introverted young man finding happiness and positivity in life through the stories of two couples.
   - **Cast:** Ashok Selvan, Ritu Varma, Aparna Balamurali, Shivathmika, Sshivada Nair

2. **Villu**
   - **Rating:** 3.8
   - **Overview:** Despite its lower rating, "Villu" offers a mix of drama, action, and comedy. The plot revolves around a son seeking revenge for his falsely framed and killed father, leading to unexpected twists and a touch of humor.
   - **Cast:** Vijay, Nayanthara, Vadivelu, Prakash Raj, Ranjitha

These are the only comedy movies with good ratings available in the context provided.
```

We could see the LLM interestingly came up with 5 choices but also highlighted stating only 2 of them were really into comedy genres.

#### GraphRAG Results:
```
🕸️ GraphRAG found movies in context:
Based on the provided graph context of comedy movies with good ratings, here are the top 5 movie recommendations:

1. **Anbe Sivam**
   - **Rating:** 7.6
   - **Overview:** Anbarasu and Nallasivam, two contrasting characters, are brought together by fate and embark on a journey that intertwines their lives.
   - **Reasoning:** Since you are looking for comedy movies with good ratings, "Anbe Sivam" stands out with its high rating of 7.6. The movie features Kamal Haasan, known for his versatile acting skills, which adds to the quality of the comedy genre.

2. **Michael Madana Kama Rajan**
   - **Rating:** 7.2
   - **Overview:** This movie follows the story of quadruplets who were separated at birth and later reunite, leading to hilarious situations.
   - **Reasoning:** With a rating of 7.2, "Michael Madana Kama Rajan" is another comedy gem that showcases Kamal Haasan's talent. The plot revolving around multiple characters played by the same actor adds a unique and entertaining element to the film.

3. **Siva Manasula Sakthi**
   - **Rating:** 6.6
   - **Overview:** Siva and Sakthi initially plan revenge but end up falling for each other, leading to a blend of comedy and romance.
   - **Reasoning:** While slightly lower in rating, at 6.6, "Siva Manasula Sakthi" offers a mix of comedy and romance, making it a light-hearted watch. The movie features Jiiva, known for his charismatic performances, adding charm to the comedic elements.

4. **Nitham Oru Vaanam**
   - **Rating:** 6.6
   - **Overview:** An introverted man finds solace in the stories of others after a heartbreak, leading to a journey of self-discovery.
   - **Reasoning:** With a rating matching "Siva Manasula Sakthi" at 6.6, "Nitham Oru Vaanam" presents a different take on comedy by intertwining elements of self-growth and positivity. Jiiva's portrayal adds depth to the comedic narrative.

5. **Don**
   - **Rating:** 6.3
   - **Overview:** A youngster's journey
```

We could see it almost picked only the comedy movies even with the smallest dataset of 33 movies we had fed it with reinstating that the relationship data was adding significant value.


## Conclusion
`Context` is everything to a LLM and a good model fed with as much context as possible yields better results and this demonstration with RAG vs GraphRAG is the proof for it.
