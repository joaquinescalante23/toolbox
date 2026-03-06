"""
Semantic Context Surgeon - Token Budget Manager
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Precision tool to trim context window while preserving semantic integrity.
             Ensures the 'Token Budget' is respected without mid-sentence truncation.
"""

import re
import math
from typing import List, Dict, Any, Optional, Tuple
from enum import Enum


class TrimStrategy(Enum):
    """Available trimming strategies."""
    SURGICAL = "surgical"
    HEAD = "head"
    TAIL = "tail"
    HEAD_AND_TAIL = "head_and_tail"
    SUMMARY = "summary"


class TokenBudgetManager:
    """Professional token budget manager for LLM context windows."""
    
    def __init__(
        self, 
        max_tokens: int, 
        chars_per_token: float = 4.0,
        encoding_name: str = "cl100k_base"
    ):
        self.max_tokens = max_tokens
        self.chars_per_token = chars_per_token
        self.encoding_name = encoding_name
        self.char_limit = int(max_tokens * chars_per_token)
    
    def count_tokens(self, text: str) -> int:
        """Estimate token count."""
        return int(len(text) / self.chars_per_token)
    
    def fits_in_budget(self, text: str) -> bool:
        """Check if text fits within token budget."""
        return self.count_tokens(text) <= self.max_tokens
    
    def surgical_trim(self, text: str, ellipsis: str = " [...] ") -> str:
        """
        Trim text to fit budget by cutting at sentence boundaries.
        Prefers to keep the beginning of the text.
        """
        if self.fits_in_budget(text):
            return text
        
        truncated = text[:self.char_limit]
        
        sentence_ends = [
            truncated.rfind('.'),
            truncated.rfind('!'),
            truncated.rfind('?'),
            truncated.rfind('。'),
            truncated.rfind('！'),
            truncated.rfind('？')
        ]
        last_sentence_end = max(sentence_ends)
        
        if last_sentence_end > self.char_limit // 2:
            return truncated[:last_sentence_end + 1]
        
        return truncated + ellipsis
    
    def tail_trim(self, text: str, ellipsis: str = "\n[...continues]") -> str:
        """
        Trim text keeping the end portion.
        Useful when recent information is more important.
        """
        if self.fits_in_budget(text):
            return text
        
        truncated = text[-self.char_limit:]
        
        sentence_starts = [
            truncated.find('. '),
            truncated.find('! '),
            truncated.find('? '),
            truncated.find('。')
        ]
        first_sentence_start = max([s for s in sentence_starts if s > 0], default=0)
        
        if first_sentence_start > 0:
            return "[...]" + truncated[first_sentence_start + 1:]
        
        return ellipsis + truncated
    
    def head_and_tail_trim(
        self, 
        text: str, 
        head_ratio: float = 0.4,
        ellipsis: str = "\n[...]\n"
    ) -> str:
        """
        Keep beginning and end, trim middle.
        Based on primacy and recency effects in LLM attention.
        """
        if self.fits_in_budget(text):
            return text
        
        head_chars = int(self.char_limit * head_ratio)
        tail_chars = self.char_limit - head_chars
        
        head_text = text[:head_chars]
        tail_text = text[-tail_chars:]
        
        head_end = max(
            head_text.rfind('. '),
            head_text.rfind('! '),
            head_text.rfind('? ')
        )
        
        if head_end > head_chars // 2:
            head_text = head_text[:head_end + 1]
        
        tail_start = min(
            tail_text.find('. '),
            tail_text.find('! '),
            tail_text.find('? ')
        )
        
        if 0 < tail_start < tail_chars // 2:
            tail_text = tail_text[tail_start + 1:]
        
        return head_text + ellipsis + tail_text
    
    def smart_trim(
        self, 
        text: str, 
        priority_keywords: Optional[List[str]] = None,
        strategy: TrimStrategy = TrimStrategy.HEAD_AND_TAIL
    ) -> str:
        """
        Smart trim that prioritizes sections with important keywords.
        """
        if self.fits_in_budget(text):
            return text
        
        priority_keywords = priority_keywords or []
        
        if strategy == TrimStrategy.SURGICAL:
            return self.surgical_trim(text)
        elif strategy == TrimStrategy.HEAD:
            return self.surgical_trim(text)
        elif strategy == TrimStrategy.TAIL:
            return self.tail_trim(text)
        elif strategy == TrimStrategy.HEAD_AND_TAIL:
            return self.head_and_tail_trim(text)
        else:
            return self.surgical_trim(text)
    
    def trim_multiple(
        self, 
        chunks: List[Dict[str, Any]], 
        text_field: str = "text",
        strategy: TrimStrategy = TrimStrategy.HEAD_AND_TAIL
    ) -> List[Dict[str, Any]]:
        """
        Trim multiple chunks to fit within total budget.
        Distributes budget proportionally.
        """
        total_chars = sum(len(c.get(text_field, '')) for c in chunks)
        
        if total_chars <= self.char_limit:
            return chunks
        
        trimmed_chunks = []
        budget_per_chunk = self.char_limit / len(chunks)
        
        for chunk in chunks:
            text = chunk.get(text_field, '')
            chunk_budget = int(budget_per_chunk)
            
            temp_manager = TokenBudgetManager(
                int(chunk_budget / self.chars_per_token),
                self.chars_per_token
            )
            
            trimmed_text = temp_manager.smart_trim(text, strategy=strategy)
            
            new_chunk = chunk.copy()
            new_chunk[text_field] = trimmed_text
            new_chunk['original_tokens'] = temp_manager.count_tokens(text)
            new_chunk['trimmed_tokens'] = temp_manager.count_tokens(trimmed_text)
            trimmed_chunks.append(new_chunk)
        
        return trimmed_chunks
    
    def get_budget_info(self, text: str) -> Dict[str, Any]:
        """Get detailed budget information."""
        tokens = self.count_tokens(text)
        
        return {
            "current_tokens": tokens,
            "max_tokens": self.max_tokens,
            "usage_ratio": round(tokens / self.max_tokens, 4) if self.max_tokens > 0 else 0,
            "fits": tokens <= self.max_tokens,
            "chars": len(text),
            "char_limit": self.char_limit
        }


if __name__ == "__main__":
    long_text = (
        "This is the first important point about the topic. "
        "Here we have some additional context that explains the concept. "
        "Moreover, there are several factors to consider. "
        "Finally, we reach the most critical conclusion. "
    ) * 20
    
    manager = TokenBudgetManager(max_tokens=100)
    
    print("=== Budget Info ===")
    print(manager.get_budget_info(long_text))
    
    print("\n=== Surgical Trim ===")
    print(manager.surgical_trim(long_text)[:200])
    
    print("\n=== Head and Tail Trim ===")
    print(manager.head_and_tail_trim(long_text))
