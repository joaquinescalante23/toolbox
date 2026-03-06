"""
Semantic Context Surgeon - Chunk Overlap Handler
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Handles chunk overlaps during text splitting. Manages redundant
             content, preserves context across boundaries, and optimizes 
             for minimal redundancy while maintaining continuity.
"""

import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter
import json


class ChunkOverlapHandler:
    """Handler for chunk overlaps and boundaries."""
    
    def __init__(self, overlap_chars: int = 50, min_chunk_size: int = 100):
        self.overlap_chars = overlap_chars
        self.min_chunk_size = min_chunk_size
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        return re.findall(r'\b\w+\b', text.lower())
    
    def _find_boundary(self, text: str, position: int) -> int:
        """Find a natural boundary near position."""
        for punct in ['. ', '! ', '? ', '\n', ', ']:
            boundary = text.rfind(punct, 0, position)
            if boundary > position - 50:
                return boundary + len(punct)
        
        boundary = text.rfind(' ', 0, position)
        if boundary > position - 30:
            return boundary
        
        return position
    
    def split_with_overlap(
        self, 
        text: str, 
        chunk_size: int,
        overlap_type: str = "sentence"
    ) -> List[Dict[str, Any]]:
        """
        Split text into overlapping chunks.
        
        overlap_type: "sentence", "word", "char", "none"
        """
        if len(text) <= chunk_size:
            return [{"id": 0, "text": text, "start": 0, "end": len(text)}]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end >= len(text):
                chunks.append({
                    "id": chunk_id,
                    "text": text[start:],
                    "start": start,
                    "end": len(text)
                })
                break
            
            if overlap_type == "sentence":
                boundary = self._find_boundary(text, end)
            elif overlap_type == "word":
                boundary = text.rfind(' ', 0, end)
            elif overlap_type == "char":
                boundary = end - self.overlap_chars
            else:
                boundary = end
            
            chunk_text = text[start:boundary]
            
            if len(chunk_text) >= self.min_chunk_size:
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "start": start,
                    "end": boundary
                })
                chunk_id += 1
            
            if overlap_type == "none":
                start = end
            else:
                start = boundary
        
        return chunks
    
    def merge_overlapping_chunks(
        self, 
        chunks: List[Dict[str, Any]],
        similarity_threshold: float = 0.8
    ) -> List[Dict[str, Any]]:
        """Merge chunks that have significant overlap."""
        if len(chunks) <= 1:
            return chunks
        
        merged = [chunks[0].copy()]
        
        for chunk in chunks[1:]:
            last_merged = merged[-1]
            
            overlap = self._calculate_overlap(
                last_merged.get('text', ''),
                chunk.get('text', '')
            )
            
            if overlap >= similarity_threshold:
                merged[-1] = {
                    "id": merged[-1]['id'],
                    "text": last_merged['text'] + ' ' + chunk['text'],
                    "start": last_merged.get('start', 0),
                    "end": chunk.get('end', 0)
                }
            else:
                merged.append(chunk.copy())
        
        return merged
    
    def _calculate_overlap(self, text1: str, text2: str) -> float:
        """Calculate overlap between two texts."""
        words1 = set(self._tokenize(text1))
        words2 = set(self._tokenize(text2))
        
        if not words1 or not words2:
            return 0.0
        
        overlap = len(words1 & words2)
        return overlap / min(len(words1), len(words2))
    
    def deduplicate_overlaps(
        self, 
        chunks: List[Dict[str, Any]],
        dedup_threshold: float = 0.9
    ) -> List[Dict[str, Any]]:
        """Remove near-duplicate chunks."""
        if not chunks:
            return []
        
        unique = []
        
        for chunk in chunks:
            is_duplicate = False
            
            for unique_chunk in unique:
                overlap = self._calculate_overlap(
                    unique_chunk.get('text', ''),
                    chunk.get('text', '')
                )
                
                if overlap >= dedup_threshold:
                    is_duplicate = True
                    unique_chunk['duplicates'] = unique_chunk.get('duplicates', 0) + 1
                    break
            
            if not is_duplicate:
                unique.append(chunk.copy())
        
        return unique


class SmartChunker:
    """Smart chunking with semantic awareness."""
    
    def __init__(
        self, 
        chunk_size: int = 500,
        overlap: int = 100,
        min_sentences: int = 1
    ):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.min_sentences = min_sentences
    
    def _split_sentences(self, text: str) -> List[str]:
        """Split text into sentences."""
        sentences = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def chunk_by_sentences(self, text: str) -> List[Dict[str, Any]]:
        """Chunk text by sentences, respecting size limits."""
        sentences = self._split_sentences(text)
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        start_idx = 0
        
        for i, sentence in enumerate(sentences):
            sentence_size = len(sentence)
            
            if current_size + sentence_size > self.chunk_size and current_chunk:
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "id": chunk_id,
                    "text": chunk_text,
                    "sentence_count": len(current_chunk),
                    "start": start_idx,
                    "end": start_idx + len(chunk_text)
                })
                
                overlap_text = ' '.join(current_chunk[-self.min_sentences:])
                overlap_size = len(overlap_text)
                
                if overlap_size > 0 and overlap_size < self.chunk_size // 2:
                    current_chunk = overlap_text.split()
                    current_size = overlap_size
                else:
                    current_chunk = []
                    current_size = 0
                
                start_idx += len(chunk_text)
                chunk_id += 1
            
            current_chunk.append(sentence)
            current_size += sentence_size + 1
        
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "sentence_count": len(current_chunk),
                "start": start_idx,
                "end": start_idx + len(chunk_text)
            })
        
        return chunks
    
    def chunk_by_paragraphs(self, text: str) -> List[Dict[str, Any]]:
        """Chunk text by paragraphs."""
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_size = 0
        chunk_id = 0
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            if current_size + len(para) > self.chunk_size and current_chunk:
                chunks.append({
                    "id": chunk_id,
                    "text": '\n\n'.join(current_chunk),
                    "paragraph_count": len(current_chunk),
                    "chunk_id": chunk_id
                })
                
                if self.overlap > 0 and len(current_chunk) > 1:
                    current_chunk = current_chunk[-1:]
                else:
                    current_chunk = []
                
                current_size = 0
                chunk_id += 1
            
            current_chunk.append(para)
            current_size += len(para) + 2
        
        if current_chunk:
            chunks.append({
                "id": chunk_id,
                "text": '\n\n'.join(current_chunk),
                "paragraph_count": len(current_chunk),
                "chunk_id": chunk_id
            })
        
        return chunks


class SlidingWindowChunker:
    """Sliding window chunking for maximum context preservation."""
    
    def __init__(self, window_size: int = 200, stride: int = 100):
        self.window_size = window_size
        self.stride = stride
    
    def chunk(self, text: str) -> List[Dict[str, Any]]:
        """Create chunks using sliding window."""
        if len(text) <= self.window_size:
            return [{"id": 0, "text": text, "start": 0, "end": len(text)}]
        
        chunks = []
        start = 0
        chunk_id = 0
        
        while start + self.window_size <= len(text):
            chunks.append({
                "id": chunk_id,
                "text": text[start:start + self.window_size],
                "start": start,
                "end": start + self.window_size
            })
            
            start += self.stride
            chunk_id += 1
        
        if start < len(text):
            chunks.append({
                "id": chunk_id,
                "text": text[start:],
                "start": start,
                "end": len(text)
            })
        
        return chunks


if __name__ == "__main__":
    text = "This is the first sentence. Here is the second one. " * 50
    
    print("=== Chunk by Sentences ===")
    chunker = SmartChunker(chunk_size=200)
    chunks = chunker.chunk_by_sentences(text)
    print(f"Created {len(chunks)} chunks")
    
    print("\n=== Sliding Window ===")
    slider = SlidingWindowChunker(window_size=100, stride=50)
    chunks = slider.chunk(text)
    print(f"Created {len(chunks)} chunks")
    
    print("\n=== Overlap Handler ===")
    handler = ChunkOverlapHandler(overlap_chars=30)
    chunks = handler.split_with_overlap(text * 3, 200, overlap_type="sentence")
    print(f"Created {len(chunks)} chunks")
    
    print("\n=== Deduplication ===")
    test_chunks = [
        {"text": "This is some content about AI and machine learning."},
        {"text": "This is some content about AI and machine learning."},
        {"text": "Completely different content about weather."},
    ]
    deduped = handler.deduplicate_overlaps(test_chunks, 0.8)
    print(f"Kept {len(deduped)} unique chunks")
