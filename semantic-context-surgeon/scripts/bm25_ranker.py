"""
Semantic Context Surgeon - BM25 Ranker
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Professional BM25 ranking algorithm implementation for RAG pipelines.
             BM25 is a probabilistic ranking function used for document retrieval.
"""

import math
import re
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter, defaultdict
import json


class BM25Ranker:
    """BM25 ranking for semantic search."""
    
    def __init__(
        self, 
        query: str, 
        context_chunks: List[Dict[str, Any]],
        k1: float = 1.5,
        b: float = 0.75
    ):
        self.query = query
        self.chunks = context_chunks
        self.k1 = k1
        self.b = b
        
        self.corpus_size = len(context_chunks)
        self.avgdl = 0
        self.doc_freqs = {}
        self.idf = {}
        self.doc_len = []
        self.doc_token_counts = []
        
        if self.corpus_size > 0:
            self._initialize()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        tokens = text.split()
        return [t for t in tokens if len(t) > 1]
    
    def _initialize(self):
        """Initialize BM25 parameters."""
        doc_freqs = Counter()
        doc_lengths = []
        
        for chunk in self.chunks:
            text = chunk.get('text', '')
            tokens = self._tokenize(text)
            doc_lengths.append(len(tokens))
            
            freq = Counter(tokens)
            self.doc_token_counts.append(freq)
            
            for term in freq.keys():
                doc_freqs[term] += 1
        
        self.doc_len = doc_lengths
        self.avgdl = sum(doc_lengths) / self.corpus_size if self.corpus_size > 0 else 0
        
        for term, freq in doc_freqs.items():
            self.idf[term] = math.log((self.corpus_size - freq + 0.5) / (freq + 0.5) + 1)
    
    def _score_single(self, query_terms: List[str], doc_idx: int) -> float:
        """Calculate BM25 score for a single document."""
        doc_len = self.doc_len[doc_idx]
        doc_freqs = self.doc_token_counts[doc_idx]
        
        score = 0.0
        
        for term in query_terms:
            if term not in doc_freqs:
                continue
            
            freq = doc_freqs[term]
            idf = self.idf.get(term, 0)
            
            numerator = freq * (self.k1 + 1)
            denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            
            score += idf * (numerator / denominator)
        
        return score
    
    def rank(self, top_k: int = 5) -> List[Dict[str, Any]]:
        """Rank chunks by BM25 score."""
        if not self.chunks:
            return []
        
        query_terms = self._tokenize(self.query)
        
        if not query_terms:
            return self.chunks[:top_k]
        
        scores = []
        for idx in range(self.corpus_size):
            score = self._score_single(query_terms, idx)
            scores.append({
                'idx': idx,
                'chunk': self.chunks[idx],
                'bm25_score': round(score, 4)
            })
        
        ranked = sorted(scores, key=lambda x: x['bm25_score'], reverse=True)
        
        results = []
        for s in ranked[:top_k]:
            result = s['chunk'].copy()
            result['bm25_score'] = s['bm25_score']
            results.append(result)
        
        return results
    
    def get_term_stats(self) -> Dict[str, Any]:
        """Get term statistics from the corpus."""
        all_terms = set()
        for doc_freqs in self.doc_token_counts:
            all_terms.update(doc_freqs.keys())
        
        return {
            'corpus_size': self.corpus_size,
            'avg_document_length': round(self.avgdl, 2),
            'unique_terms': len(all_terms),
            'total_terms': sum(sum(d.values()) for d in self.doc_token_counts),
            'query_terms': self._tokenize(self.query),
            'top_idf_terms': sorted(self.idf.items(), key=lambda x: x[1], reverse=True)[:10]
        }


class BM25PlusRanker(BM25Ranker):
    """BM25+ ranking - handles term frequency saturation better."""
    
    def __init__(self, query: str, context_chunks: List[Dict[str, Any]], k1: float = 1.5, b: float = 0.75, delta: float = 1.0):
        self.delta = delta
        super().__init__(query, context_chunks, k1, b)
    
    def _score_single(self, query_terms: List[str], doc_idx: int) -> float:
        """Calculate BM25+ score."""
        doc_len = self.doc_len[doc_idx]
        doc_freqs = self.doc_token_counts[doc_idx]
        
        score = 0.0
        
        for term in query_terms:
            if term not in doc_freqs:
                continue
            
            freq = doc_freqs[term]
            idf = self.idf.get(term, 0)
            
            numerator = freq + self.delta
            denominator = freq + self.k1 * (1 - self.b + self.b * doc_len / self.avgdl)
            
            score += idf * (numerator / denominator)
        
        return score


if __name__ == "__main__":
    query = "Neo4j optimization indexing"
    chunks = [
        {"id": 1, "text": "Neo4j indexing strategies improve query performance significantly."},
        {"id": 2, "text": "Graph databases like Neo4j excel at relationship queries."},
        {"id": 3, "text": "Proper indexing is crucial for database optimization."},
        {"id": 4, "text": "The weather today is sunny and warm."},
        {"id": 5, "text": "Vector search can optimize RAG retrieval in Neo4j."},
    ]
    
    ranker = BM25Ranker(query, chunks)
    
    print("=== BM25 Ranking ===")
    results = ranker.rank(top_k=3)
    for r in results:
        print(f"  ID {r['id']}: score={r['bm25_score']}")
    
    print("\n=== Term Stats ===")
    stats = ranker.get_term_stats()
    print(f"  Corpus size: {stats['corpus_size']}")
    print(f"  Avg doc length: {stats['avg_document_length']}")
    print(f"  Query terms: {stats['query_terms']}")
    print(f"  Top IDF terms: {stats['top_idf_terms'][:5]}")
