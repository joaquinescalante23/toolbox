# Graph-RAG Density Optimizer (GRDO)
**Advanced Knowledge Graph refinement and semantic node fusion for Hybrid RAG agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Author: joaquinescalante23](https://img.shields.io/badge/Author-joaquinescalante23-blue.svg)](https://github.com/joaquinescalante23)

## Overview

**GRDO** is a professional-grade optimization suite for Knowledge Graphs (Neo4j) used in Hybrid RAG systems. It focuses on **Knowledge Density**—the science of reducing graph noise while maximizing semantic connectivity.

### Key Features

| Feature | Description |
|---------|-------------|
| **Semantic Node Fusion** | Automatically identifies and merges redundant nodes using cosine similarity |
| **Taxonomy Building** | Detects hierarchical (IS_A) relationships between concepts |
| **Topology Audit** | Identifies isolated nodes, hubs, and bridge nodes using degree centrality |
| **Concept Clustering** | Groups related concepts using transitive similarity |
| **Cypher Generator** | Produces optimized MERGE, DELETE, and relationship queries |

## Installation

```bash
git clone https://github.com/joaquinescalante23/graph-rag-density-optimizer.git
cd graph-rag-density-optimizer

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate
```

## Usage

### Audit Graph Topology

```bash
python3 cli.py audit samples/graph_data.json -o audit_report.json -q
```

### Perform Semantic Node Merging

```bash
python3 cli.py merge samples/nodes_with_embeddings.json -t 0.95 -q
```

### Build Taxonomy Hierarchy

```bash
python3 cli.py taxonomy samples/nodes_with_matrix.json -q
```

### Programmatic Usage

```python
from scripts.merger import SemanticMerger
from scripts.audit import TopologyAudit
from scripts.taxonomy import TaxonomyBuilder

# Semantic Merging
merger = SemanticMerger(nodes, threshold=0.95)
duplicates = merger.find_duplicates()
cypher = merger.generate_cypher_merge(duplicates)

# Topology Audit
audit = TopologyAudit(nodes, edges)
report = audit.audit_report()

# Taxonomy Building
taxonomy = TaxonomyBuilder(nodes, similarity_matrix)
hierarchies = taxonomy.detect_hierarchy()
```

## Architecture

```
graph-rag-density-optimizer/
├── cli.py                 # Main CLI orchestrator
├── SKILL.md              # OpenCode skill definition
├── README.md
├── scripts/
│   ├── merger.py         # Semantic node merging with cosine similarity
│   ├── audit.py          # Topology analysis and health metrics
│   └── taxonomy.py       # Hierarchy detection and clustering
├── references/
│   └── graph_rag_axioms.md
└── samples/              # Sample data for testing
```

## Detected Issues

GRDO identifies these common Knowledge Graph problems:

| Issue | Detection Method | Recommendation |
|-------|------------------|----------------|
| **Isolated Nodes** | Degree <= 1 | DELETE |
| **Redundant Nodes** | Cosine similarity > 0.95 | MERGE |
| **Missing Hierarchy** | Similarity 0.85-0.95 | CREATE IS_A |
| **Concept Clusters** | Transitive similarity > 0.7 | LINK SAME_CLUSTER |

## Theoretical Foundation

The project addresses the "Fragmentation Crisis" in Hybrid RAG systems.

See `references/graph_rag_axioms.md` for detailed theory.

## Contributing

Contributions are welcome! Please open a PR.

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

**Joaquín Escalante** - [@joaquinescalante23](https://github.com/joaquinescalante23)
