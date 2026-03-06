---
name: graph-rag-density-optimizer
description: Professional-grade suite for Knowledge Graph refinement in Hybrid RAG systems. Use this skill to (1) Merge semantically identical nodes using cosine similarity on embeddings, (2) Prune isolated/hub/bridge nodes from graph topology, (3) Build taxonomy hierarchies with IS_A relationships, (4) Generate optimized Cypher queries.
---

# Graph-RAG Density Optimizer (GRDO)
**Developed by: [joaquinescalante23](https://github.com/joaquinescalante23)**

Professional-grade optimization suite for Knowledge Graphs (Neo4j) in Hybrid RAG systems.

## Quick Start

### CLI Usage
```bash
# Audit graph topology
python3 cli.py audit samples/graph_data.json -q

# Semantic node merging
python3 cli.py merge samples/nodes.json -t 0.95 -q

# Build taxonomy
python3 cli.py taxonomy samples/nodes.json -q
```

### Programmatic Usage
```python
from scripts.merger import SemanticMerger
from scripts.audit import TopologyAudit
from scripts.taxonomy import TaxonomyBuilder

merger = SemanticMerger(nodes, 0.95)
audit = TopologyAudit(nodes, edges)
taxonomy = TaxonomyBuilder(nodes, similarity_matrix)
```

## Features

| Module | Features |
|--------|----------|
| **merger.py** | Cosine similarity, similarity matrix, duplicate detection, related concepts, Cypher generation |
| **audit.py** | Degree centrality, in/out degrees, isolated/hub/bridge nodes, betweenness, delete queries |
| **taxonomy.py** | Hierarchy detection, IS_A relationships, taxonomy tree, concept clustering |

## Detected Issues

- **Isolated Nodes**: Degree <= 1
- **Redundant Nodes**: Cosine similarity > 0.95
- **Missing Hierarchy**: Similarity 0.85-0.95
- **Concept Clusters**: Transitive similarity > 0.7

## References

- `references/graph_rag_axioms.md` - Theoretical foundation
