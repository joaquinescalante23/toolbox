"""
Semantic Context Surgeon - Embedding Ranker
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Semantic ranking using embeddings. Uses sentence-transformers if available,
             otherwise falls back to TF-IDF based semantic matching.
"""

import math
import json
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import re

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


class EmbeddingRanker:
    """Semantic ranker using embeddings."""
    
    def __init__(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]],
        model_name: str = "all-MiniLM-L6-v2",
        use_fallback: bool = True
    ):
        self.query = query
        self.chunks = context_chunks
        self.model_name = model_name
        self.model = None
        self.use_fallback = use_fallback or not SENTENCE_TRANSFORMERS_AVAILABLE
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model."""
        if SENTENCE_TRANSFORMERS_AVAILABLE and not self.use_fallback:
            try:
                self.model = SentenceTransformer(self.model_name)
                print(f"Using model: {self.model_name}")
            except Exception as e:
                print(f"Failed to load {self.model_name}: {e}. Using fallback.")
                self.use_fallback = True
        
        if self.use_fallback and SKLEARN_AVAILABLE:
            print("Using TF-IDF fallback for embeddings")
        elif self.use_fallback:
            print("Warning: No embedding backend available")
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for texts."""
        if self.model and not self.use_fallback:
            return self.model.encode(texts).tolist()
        
        if SKLEARN_AVAILABLE:
            return self._get_tfidf_embeddings(texts)
        
        return [[0.0] * 384 for _ in texts]
    
    def _get_tfidf_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate TF-IDF based pseudo-embeddings."""
        vectorizer = TfidfVectorizer(
            max_features=384,
            stop_words='english',
            ngram_range=(1, 2)
        )
        
        try:
            tfidf_matrix = vectorizer.fit_transform(texts)
            embeddings = tfidf_matrix.toarray().tolist()
            
            normalized = []
            for emb in embeddings:
                norm = math.sqrt(sum(x * x for x in emb))
                if norm > 0:
                    normalized.append([x / norm for x in emb])
                else:
                    normalized.append(emb)
            return normalized
        except:
            return [[0.0] * 384 for _ in texts]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0
        
        dot = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if not norm1 or not norm2:
            return 0.0
        
        return dot / (norm1 * norm2)
    
    def rank(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank chunks by embedding similarity."""
        if not self.chunks:
            return []
        
        texts = [self.query] + [c.get('text', '') for c in self.chunks]
        embeddings = self._get_embeddings(texts)
        
        query_embedding = embeddings[0]
        chunk_embeddings = embeddings[1:]
        
        results = []
        for idx, (chunk, emb) in enumerate(zip(self.chunks, chunk_embeddings)):
            similarity = self._cosine_similarity(query_embedding, emb)
            
            result = chunk.copy()
            result['embedding_score'] = round(similarity, 4)
            results.append(result)
        
        ranked = sorted(results, key=lambda x: x['embedding_score'], reverse=True)
        return ranked[:top_k]
    
    def rank_with_diversity(self, top_k: int = 5, diversity_weight: float = 0.3) -> List[Dict[str, Any]]:
        """Rank with MMR (Maximal Marginal Relevance) for diversity."""
        if not self.chunks:
            return []
        
        texts = [self.query] + [c.get('text', '') for c in self.chunks]
        embeddings = self._get_embeddings(texts)
        
        query_embedding = embeddings[0]
        
        scores = []
        for idx, emb in enumerate(embeddings[1:]):
            relevance = self._cosine_similarity(query_embedding, emb)
            scores.append({
                'idx': idx,
                'chunk': self.chunks[idx],
                'relevance': relevance,
                'embedding': emb
            })
        
        selected = []
        remaining = scores.copy()
        
        while len(selected) < top_k and remaining:
            if not selected:
                best = max(remaining, key=lambda x: x['relevance'])
            else:
                best = None
                best_score = -1
                
                for candidate in remaining:
                    relevance = candidate['relevance']
                    
                    max_sim_to_selected = max(
                        self._cosine_similarity(candidate['embedding'], s['embedding'])
                        for s in selected
                    ) if selected else 0
                    
                    mmr_score = (1 - diversity_weight) * relevance + diversity_weight * max_sim_to_selected
                    
                    if mmr_score > best_score:
                        best_score = mmr_score
                        best = candidate
            
            if best:
                selected.append(best)
                remaining.remove(best)
        
        results = []
        for s in selected:
            result = s['chunk'].copy()
            result['embedding_score'] = round(s['relevance'], 4)
            results.append(result)
        
        return results


if __name__ == "__main__":
    query = "How to optimize Neo4j for RAG?"
    chunks = [
        {"id": 1, "text": "Neo4j optimization involves indexing strategies."},
        {"id": 2, "text": "Graph databases are great for relationship queries."},
        {"id": 3, "text": "RAG systems benefit from vector search."},
        {"id": 4, "text": "Neo4j indexing can significantly improve query performance."},
        {"id": 5, "text": "The weather is nice today."},
    ]
    
    ranker = EmbeddingRanker(query, chunks)
    
    print("=== Simple Ranking ===")
    results = ranker.rank(top_k=3)
    for r in results:
        print(f"  ID {r['id']}: score={r['embedding_score']}")
    
    print("\n=== MMR Diversity Ranking ===")
    results = ranker.rank_with_diversity(top_k=3, diversity_weight=0.3)
    for r in results:
        print(f"  ID {r['id']}: score={r['embedding_score']}")
