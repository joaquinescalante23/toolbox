"""
Semantic Context Surgeon - Context Ranker
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Professional re-ranking utility for RAG pipelines. Uses semantic 
             relevance scoring to prioritize high-value context chunks.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter


class ContextRanker:
    """Professional context ranker for RAG pipelines."""
    
    def __init__(self, query: str, context_chunks: List[Dict[str, Any]]):
        self.query = query
        self.chunks = context_chunks
        self.query_terms = self._tokenize(query)
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [t for t in text.split() if len(t) > 1]
    
    def _get_relevance_score(self, chunk_text: str) -> float:
        """Calculate semantic relevance score using keyword density and overlap."""
        chunk_terms = self._tokenize(chunk_text)
        
        if not chunk_terms or not self.query_terms:
            return 0.0
        
        query_set = set(self.query_terms)
        chunk_set = set(chunk_terms)
        
        overlap = len(query_set & chunk_set)
        density = overlap / len(query_set)
        
        return round(density, 4)
    
    def _get_position_score(self, position: int, total: int) -> float:
        """
        Calculate position score based on primacy/recency effect.
        Chunks at the beginning and end get higher scores.
        """
        if total <= 1:
            return 1.0
        
        normalized_pos = position / (total - 1) if total > 1 else 0
        position_score = 1.0 - abs(0.5 - normalized_pos)
        
        return round(position_score * 2, 4)
    
    def _get_length_score(self, chunk_text: str, avg_length: float) -> float:
        """
        Calculate length score.
        Chunks too short or too long get penalized.
        """
        length = len(chunk_text.split())
        
        if length == 0:
            return 0.0
        
        if avg_length == 0:
            return 0.5
        
        length_ratio = length / avg_length
        
        if 0.5 <= length_ratio <= 1.5:
            return 1.0
        elif length_ratio < 0.5:
            return length_ratio * 2
        else:
            return max(0.3, 1.0 - (length_ratio - 1.5) * 0.3)
    
    def rank(
        self, 
        top_k: int = 5, 
        min_score: float = 0.0,
        use_position_weight: float = 0.2,
        use_length_weight: float = 0.1
    ) -> List[Dict[str, Any]]:
        """Rank chunks by composite relevance score."""
        if not self.chunks:
            return []
        
        avg_length = sum(len(c.get('text', '').split()) for c in self.chunks) / len(self.chunks)
        
        scored_chunks = []
        for idx, chunk in enumerate(self.chunks):
            chunk_text = chunk.get('text', '')
            
            relevance = self._get_relevance_score(chunk_text)
            position = self._get_position_score(idx, len(self.chunks))
            length = self._get_length_score(chunk_text, avg_length)
            
            composite_score = (
                relevance * (1.0 - use_position_weight - use_length_weight) +
                position * use_position_weight +
                length * use_length_weight
            )
            
            if composite_score >= min_score:
                scored_chunk = chunk.copy()
                scored_chunk['relevance_score'] = round(relevance, 4)
                scored_chunk['position_score'] = position
                scored_chunk['length_score'] = round(length, 4)
                scored_chunk['composite_score'] = round(composite_score, 4)
                scored_chunks.append(scored_chunk)
        
        ranked = sorted(
            scored_chunks, 
            key=lambda x: x['composite_score'], 
            reverse=True
        )
        
        return ranked[:top_k]
    
    def rank_and_deduplicate(
        self, 
        top_k: int = 5, 
        similarity_threshold: float = 0.9
    ) -> List[Dict[str, Any]]:
        """Rank chunks and remove near-duplicates."""
        ranked = self.rank(top_k=top_k * 2)
        
        if not ranked:
            return []
        
        unique_chunks = []
        seen_texts = []
        
        for chunk in ranked:
            text = chunk.get('text', '').lower()
            
            is_duplicate = False
            for seen in seen_texts:
                similarity = self._text_similarity(text, seen)
                if similarity >= similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_chunks.append(chunk)
                seen_texts.append(text)
            
            if len(unique_chunks) >= top_k:
                break
        
        return unique_chunks
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate Jaccard similarity between two texts."""
        set1 = set(self._tokenize(text1))
        set2 = set(self._tokenize(text2))
        
        if not set1 or not set2:
            return 0.0
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
    
    def get_diversity_score(self) -> float:
        """Calculate diversity score across all chunks."""
        if not self.chunks:
            return 0.0
        
        all_terms = []
        for chunk in self.chunks:
            all_terms.extend(self._tokenize(chunk.get('text', '')))
        
        if not all_terms:
            return 0.0
        
        unique_terms = len(set(all_terms))
        total_terms = len(all_terms)
        
        return round(unique_terms / total_terms, 4)


if __name__ == "__main__":
    q = "How to optimize Neo4j for RAG?"
    data = [
        {"id": 1, "text": "To optimize Neo4j for RAG, use indexing and avoid deep path traversals."},
        {"id": 2, "text": "The weather today in Madrid is sunny with a chance of rain."},
        {"id": 3, "text": "Graph databases like Neo4j are better than SQL for relationship-heavy data in RAG."},
        {"id": 4, "text": "Neo4j performance tuning involves caching strategies and query optimization."},
    ]
    
    ranker = ContextRanker(q, data)
    results = ranker.rank(top_k=3)
    
    print("Ranked Results:")
    for r in results:
        print(f"  ID {r['id']}: score={r['composite_score']}")
    
    print(f"\nDiversity Score: {ranker.get_diversity_score()}")
