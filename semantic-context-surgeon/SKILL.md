---
name: semantic-context-surgeon
description: Precision context pruning and semantic re-ranking for RAG pipelines. Use this skill to (1) Rank context chunks by relevance with multiple algorithms (keyword, embedding, BM25), (2) Optimize chunk placement in context window, (3) Expand queries for better retrieval, (4) Handle chunk overlaps and deduplication, (5) Trim text to fit token budget.
---

# Semantic Context Surgeon (SCS)
**Developed by: [joaquinescalante23](https://github.com/joaquinescalante23)**

Comprehensive context optimization suite for RAG pipelines.

## Quick Start

### CLI Usage
```bash
# Keyword ranking
python3 cli.py rank "query" --context chunks.json -k 5

# Embedding ranking with diversity
python3 cli.py embed "query" --context chunks.json --diversity

# BM25 ranking
python3 cli.py bm25 "query" --context chunks.json

# Query expansion
python3 cli.py expand "Neo4j optimization" --context chunks.json

# Context window optimization
python3 cli.py optimize --context chunks.json --max_tokens 2000 --auto

# Chunk splitting
python3 cli.py chunk text.txt --mode sentences --chunk_size 500

# Token pruning
python3 cli.py prune text.txt -t 500 --strategy head_and_tail
```

### Programmatic Usage
```python
from scripts.ranker import ContextRanker
from scripts.embedding_ranker import EmbeddingRanker
from scripts.bm25_ranker import BM25Ranker
from scripts.query_expander import QueryExpander
from scripts.context_optimizer import ContextWindowOptimizer, PlacementStrategy
from scripts.chunk_overlap import ChunkOverlapHandler, SmartChunker
from scripts.pruner import TokenBudgetManager, TrimStrategy
```

## Features

| Module | Features |
|--------|----------|
| **ranker.py** | Composite scoring, position weighting, length scoring, deduplication |
| **embedding_ranker.py** | Sentence-transformers, TF-IDF fallback, MMR diversity |
| **bm25_ranker.py** | BM25/BM25+ ranking, term statistics |
| **query_expander.py** | Synonyms, concepts, context-based expansion |
| **context_optimizer.py** | 6 placement strategies, auto-optimization |
| **chunk_overlap.py** | Overlap handling, smart chunking, deduplication |
| **pruner.py** | Surgical/head/tail/head_and_tail trim, batch processing |

## Ranking Methods

- **Keyword**: Fast, no dependencies
- **Embedding**: Semantic similarity (sentence-transformers or TF-IDF fallback)
- **BM25**: Industry-standard probabilistic

## Context Strategies

- **horse**: Start/end, reduce middle (recommended)
- **pyramid**: More weight to middle
- **primacy**: Focus on beginning
- **recency**: Focus on end
- **equal_spaced**: Even distribution
- **focus**: Center-focused

## References

- `references/context_surgery_principles.md` - Theoretical foundation
