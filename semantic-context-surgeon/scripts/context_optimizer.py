"""
Semantic Context Surgeon - Context Window Optimizer
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Optimizes chunk placement in LLM context window based on 
             primacy/recency effects and attention distribution.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum
import json


class PlacementStrategy(Enum):
    """Context window placement strategies."""
    EQUAL_SPACED = "equal_spaced"
    PRIMACY = "primacy"
    RECENCY = "recency"
    PYRAMID = "pyramid"
    HORSE = "horse"
    FOCUS = "focus"


class ContextWindowOptimizer:
    """Optimizes chunk placement in LLM context window."""
    
    def __init__(
        self, 
        max_tokens: int,
        chars_per_token: float = 4.0
    ):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self.char_budget = int(max_tokens * chars_per_token)
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text."""
        return int(len(text) / self.chars_per_token)
    
    def _calculate_attention_weight(self, position: float, strategy: PlacementStrategy) -> float:
        """
        Calculate attention weight for a position based on strategy.
        position is normalized 0-1 (0 = start, 1 = end)
        """
        if strategy == PlacementStrategy.PRIMACY:
            return 1.0 - position * 0.5
        
        elif strategy == PlacementStrategy.RECENCY:
            return 0.5 + position * 0.5
        
        elif strategy == PlacementStrategy.EQUAL_SPACED:
            return 1.0
        
        elif strategy == PlacementStrategy.PYRAMID:
            return 1.0 - abs(position - 0.5) * 0.5
        
        elif strategy == PlacementStrategy.HORSE:
            if position < 0.25:
                return 1.0
            elif position > 0.75:
                return 1.0
            else:
                return 0.5
        
        elif strategy == PlacementStrategy.FOCUS:
            return 1.0 - abs(position - 0.5) * 0.8
        
        return 1.0
    
    def _score_chunk_placement(
        self, 
        chunk: Dict[str, Any], 
        position: float,
        strategy: PlacementStrategy
    ) -> float:
        """Score a chunk at a given position."""
        relevance = chunk.get('score', chunk.get('bm25_score', chunk.get('embedding_score', 0.5)))
        attention_weight = self._calculate_attention_weight(position, strategy)
        
        return relevance * attention_weight
    
    def optimize(
        self,
        chunks: List[Dict[str, Any]],
        strategy: PlacementStrategy = PlacementStrategy.HORSE,
        preserve_order: bool = False
    ) -> Dict[str, Any]:
        """
        Optimize chunk placement in context window.
        
        Returns the selected chunks with their optimal positions.
        """
        if not chunks:
            return {"chunks": [], "total_tokens": 0, "strategy": strategy.value}
        
        scored_chunks = []
        
        for idx, chunk in enumerate(chunks):
            text = chunk.get('text', '')
            tokens = self._estimate_tokens(text)
            
            scored_chunks.append({
                'chunk': chunk,
                'tokens': tokens,
                'original_position': idx,
                'score': chunk.get('score', chunk.get('bm25_score', chunk.get('embedding_score', 0.5)))
            })
        
        total_tokens = sum(c['tokens'] for c in scored_chunks)
        
        if total_tokens <= self.max_tokens:
            return {
                "chunks": scored_chunks,
                "total_tokens": total_tokens,
                "strategy": strategy.value,
                "fit": True
            }
        
        selected = self._select_chunks(scored_chunks, strategy, preserve_order)
        
        selected_chunks = [s['chunk'] for s in selected]
        total_tokens = sum(s['tokens'] for s in selected)
        
        return {
            "chunks": selected_chunks,
            "total_tokens": total_tokens,
            "strategy": strategy.value,
            "fit": total_tokens <= self.max_tokens,
            "dropped": len(chunks) - len(selected_chunks)
        }
    
    def _select_chunks(
        self,
        scored_chunks: List[Dict[str, Any]],
        strategy: PlacementStrategy,
        preserve_order: bool
    ) -> List[Dict[str, Any]]:
        """Select optimal chunks based on strategy."""
        candidates = scored_chunks.copy()
        selected = []
        used_tokens = 0
        
        while candidates and used_tokens < self.max_tokens:
            best_score = -1
            best_idx = 0
            
            for idx, candidate in enumerate(candidates):
                if candidate['tokens'] + used_tokens > self.max_tokens:
                    continue
                
                position = len(selected) / max(1, len(scored_chunks))
                score = self._score_chunk_placement(candidate, position, strategy)
                
                if preserve_order:
                    score *= (1.0 - idx * 0.1)
                
                if score > best_score:
                    best_score = score
                    best_idx = idx
            
            if best_score == -1:
                break
            
            selected.append(candidates[best_idx])
            used_tokens += candidates[best_idx]['tokens']
            candidates.pop(best_idx)
        
        return selected
    
    def optimize_with_positions(
        self,
        chunks: List[Dict[str, Any]],
        strategy: PlacementStrategy = PlacementStrategy.HORSE
    ) -> List[Dict[str, Any]]:
        """Optimize and return chunks with their optimal positions."""
        result = self.optimize(chunks, strategy)
        
        chunks_with_positions = []
        num_chunks = len(result['chunks'])
        
        for idx, chunk in enumerate(result['chunks']):
            position = idx / max(1, num_chunks - 1) if num_chunks > 1 else 0.5
            
            chunk_with_pos = chunk.copy()
            chunk_with_pos['optimal_position'] = round(position, 4)
            chunk_with_pos['attention_weight'] = round(
                self._calculate_attention_weight(position, strategy), 4
            )
            chunks_with_positions.append(chunk_with_pos)
        
        return chunks_with_positions
    
    def get_strategy_recommendation(self, num_chunks: int, avg_chunk_tokens: int) -> PlacementStrategy:
        """Recommend best strategy based on scenario."""
        estimated_total = num_chunks * avg_chunk_tokens
        
        if estimated_total > self.max_tokens * 1.5:
            return PlacementStrategy.HORSE
        
        if num_chunks <= 3:
            return PlacementStrategy.PYRAMID
        
        return PlacementStrategy.HORSE


class AdaptiveWindowOptimizer(ContextWindowOptimizer):
    """Adaptive optimizer that auto-selects best strategy."""
    
    def __init__(self, max_tokens: int, chars_per_token: float = 4.0):
        super().__init__(max_tokens, chars_per_token)
    
    def optimize_auto(self, chunks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Automatically select and apply best strategy."""
        if not chunks:
            return {"chunks": [], "total_tokens": 0}
        
        best_result = None
        best_score = -1
        
        strategies = [
            PlacementStrategy.HORSE,
            PlacementStrategy.PYRAMID,
            PlacementStrategy.PRIMACY,
            PlacementStrategy.RECENCY
        ]
        
        for strategy in strategies:
            result = self.optimize(chunks, strategy)
            
            if not result['fit']:
                continue
            
            total_score = sum(
                c.get('score', 0.5) * self._calculate_attention_weight(
                    i / max(1, len(result['chunks']) - 1), strategy
                )
                for i, c in enumerate(result['chunks'])
            )
            
            if total_score > best_score:
                best_score = total_score
                best_result = result
                best_result['auto_strategy'] = strategy.value
        
        if not best_result:
            best_result = self.optimize(chunks, PlacementStrategy.HORSE)
            best_result['auto_strategy'] = "horse (fallback)"
        
        return best_result


if __name__ == "__main__":
    chunks = [
        {"id": 1, "text": "Introduction to the topic. " * 20, "score": 0.9},
        {"id": 2, "text": "Important details here. " * 30, "score": 0.8},
        {"id": 3, "text": "Supporting information. " * 25, "score": 0.7},
        {"id": 4, "text": "Additional context. " * 20, "score": 0.6},
        {"id": 5, "text": "Conclusion and summary. " * 20, "score": 0.85},
    ]
    
    optimizer = ContextWindowOptimizer(max_tokens=100)
    
    print("=== Horse Strategy ===")
    result = optimizer.optimize(chunks, PlacementStrategy.HORSE)
    print(f"Selected: {len(result['chunks'])} chunks")
    print(f"Total tokens: {result['total_tokens']}")
    print(f"Fit: {result['fit']}")
    
    print("\n=== Auto Strategy ===")
    adaptive = AdaptiveWindowOptimizer(max_tokens=100)
    result = adaptive.optimize_auto(chunks)
    print(f"Strategy: {result.get('auto_strategy')}")
    print(f"Selected: {len(result['chunks'])} chunks")
