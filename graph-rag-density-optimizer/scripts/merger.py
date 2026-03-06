"""
Graph-RAG Density Optimizer - Semantic Merger
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Professional utility to fuse semantically identical nodes in Neo4j.
             Reduces graph fragmentation by merging nodes with high embedding similarity.
"""

import json
import math
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime


class SemanticMerger:
    """Professional semantic merger for Knowledge Graph nodes."""
    
    def __init__(self, node_data: List[Dict[str, Any]], similarity_threshold: float = 0.95):
        self.node_data = node_data
        self.threshold = similarity_threshold

    def calculate_cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculates cosine similarity between node embeddings."""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = math.sqrt(sum(a * a for a in vec1))
        magnitude2 = math.sqrt(sum(b * b for b in vec2))
        
        if not magnitude1 or not magnitude2:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)

    def calculate_similarity_matrix(self) -> Dict[str, Dict[str, float]]:
        """Computes pairwise similarity matrix for all nodes."""
        matrix = {}
        
        for i, n1 in enumerate(self.node_data):
            node_id = n1.get('id', f'node_{i}')
            matrix[node_id] = {}
            
            for j, n2 in enumerate(self.node_data):
                if i == j:
                    continue
                    
                target_id = n2.get('id', f'node_{j}')
                embedding1 = n1.get('embedding')
                embedding2 = n2.get('embedding')
                
                if embedding1 and embedding2:
                    sim = self.calculate_cosine_similarity(embedding1, embedding2)
                    matrix[node_id][target_id] = round(sim, 4)
        
        return matrix

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """Identifies nodes that should be merged based on semantic similarity."""
        merges = []
        
        for i in range(len(self.node_data)):
            n1 = self.node_data[i]
            embedding1 = n1.get('embedding')
            
            if not embedding1:
                continue
                
            for j in range(i + 1, len(self.node_data)):
                n2 = self.node_data[j]
                embedding2 = n2.get('embedding')
                
                if not embedding2:
                    continue
                
                sim = self.calculate_cosine_similarity(embedding1, embedding2)
                
                if sim >= self.threshold:
                    merges.append({
                        "source_id": n1.get('id', f'node_{i}'),
                        "target_id": n2.get('id', f'node_{j}'),
                        "source_name": n1.get('name', ''),
                        "target_name": n2.get('name', ''),
                        "similarity": round(sim, 4),
                        "action": "MERGE"
                    })
        
        return merges

    def find_similar_pairs_below_threshold(self, lower_threshold: float = 0.7) -> List[Dict[str, Any]]:
        """Finds similar but not identical nodes (potential related concepts)."""
        similar = []
        
        for i in range(len(self.node_data)):
            n1 = self.node_data[i]
            embedding1 = n1.get('embedding')
            
            if not embedding1:
                continue
                
            for j in range(i + 1, len(self.node_data)):
                n2 = self.node_data[j]
                embedding2 = n2.get('embedding')
                
                if not embedding2:
                    continue
                
                sim = self.calculate_cosine_similarity(embedding1, embedding2)
                
                if lower_threshold <= sim < self.threshold:
                    similar.append({
                        "node_a": n1.get('id', f'node_{i}'),
                        "node_b": n2.get('id', f'node_{j}'),
                        "similarity": round(sim, 4),
                        "action": "CONSIDER_RELATION"
                    })
        
        return similar

    def generate_cypher_merge(self, merges: List[Dict[str, Any]]) -> str:
        """Generates Cypher MERGE queries using apoc.refactor."""
        queries = []
        
        for m in merges:
            source_id = m.get('source_id', '')
            target_id = m.get('target_id', '')
            
            if source_id and target_id:
                query = (
                    f"MATCH (s {{id: '{source_id}'}}), (t {{id: '{target_id}'}}) "
                    f"CALL apoc.refactor.mergeNodes([s, t]) YIELD node "
                    f"RETURN node;"
                )
                queries.append(query)
        
        return "\n".join(queries)

    def generate_cypher_relationships(self, similar_pairs: List[Dict[str, Any]], rel_type: str = "RELATED_TO") -> str:
        """Generates Cypher queries to create relationships between similar nodes."""
        queries = []
        
        for pair in similar_pairs:
            node_a = pair.get('node_a', '')
            node_b = pair.get('node_b', '')
            
            if node_a and node_b:
                query = (
                    f"MATCH (a {{id: '{node_a}'}}), (b {{id: '{node_b}'}}) "
                    f"MERGE (a)-[:{rel_type}]->(b);"
                )
                queries.append(query)
        
        return "\n".join(queries)

    def generate_summary_stats(self) -> Dict[str, Any]:
        """Generates summary statistics about the node set."""
        nodes_with_embeddings = sum(1 for n in self.node_data if n.get('embedding'))
        
        return {
            "total_nodes": len(self.node_data),
            "nodes_with_embeddings": nodes_with_embeddings,
            "nodes_without_embeddings": len(self.node_data) - nodes_with_embeddings,
            "similarity_threshold": self.threshold,
            "potential_merges": len(self.find_duplicates()),
            "potential_relations": len(self.find_similar_pairs_below_threshold())
        }


if __name__ == "__main__":
    nodes = [
        {"id": "node1", "name": "AI", "embedding": [0.1, 0.2, 0.3]},
        {"id": "node2", "name": "Artificial Intelligence", "embedding": [0.11, 0.21, 0.31]},
        {"id": "node3", "name": "Machine Learning", "embedding": [0.8, 0.1, 0.1]},
        {"id": "node4", "name": "ML", "embedding": [0.82, 0.11, 0.12]}
    ]
    
    merger = SemanticMerger(nodes, threshold=0.95)
    
    print("=== Summary Stats ===")
    print(json.dumps(merger.generate_summary_stats(), indent=2))
    
    print("\n=== Potential Merges ===")
    duplicates = merger.find_duplicates()
    print(json.dumps(duplicates, indent=2))
    
    print("\n=== Similarity Matrix ===")
    print(json.dumps(merger.calculate_similarity_matrix(), indent=2))
    
    print("\n=== Cypher Queries ===")
    print(merger.generate_cypher_merge(duplicates))
