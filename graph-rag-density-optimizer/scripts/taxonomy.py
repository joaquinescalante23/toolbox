"""
Graph-RAG Density Optimizer - Taxonomy Builder
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Advanced utility to build hierarchical structures within a Knowledge Graph.
             Detects 'Hypernym' (parent) and 'Hyponym' (child) relationships to prevent 
             information loss during semantic merging.
"""

from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from datetime import datetime


class TaxonomyBuilder:
    """Professional taxonomy builder for Knowledge Graph hierarchies."""
    
    def __init__(self, nodes: List[Dict[str, Any]], similarity_matrix: Dict[str, Dict[str, float]]):
        self.nodes = nodes
        self.matrix = similarity_matrix
        self._node_map = {node.get('id', f'node_{i}'): node for i, node in enumerate(nodes)}

    def detect_hierarchy(
        self, 
        upper_threshold: float = 0.95, 
        lower_threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """
        Identifies potential hierarchical relationships.
        - Similarity > upper_threshold: Suggest MERGE (already handled by SemanticMerger)
        - upper_threshold > Similarity > lower_threshold: Suggest IS_A relationship
        """
        hierarchies = []
        
        for i in range(len(self.nodes)):
            n1 = self.nodes[i]
            n1_id = n1.get('id', f'node_{i}')
            n1_name = n1.get('name', '')
            
            for j in range(i + 1, len(self.nodes)):
                n2 = self.nodes[j]
                n2_id = n2.get('id', f'node_{j}')
                n2_name = n2.get('name', '')
                
                sim = self.matrix.get(n1_id, {}).get(n2_id, 0)
                
                if not sim:
                    sim = self.matrix.get(n2_id, {}).get(n1_id, 0)
                
                if not sim:
                    continue
                
                if lower_threshold <= sim < upper_threshold:
                    parent, child = self._determine_parent_child(n1_id, n2_id, n1_name, n2_name)
                    hierarchies.append({
                        "parent": parent,
                        "child": child,
                        "parent_name": n1_name if parent == n1_id else n2_name,
                        "child_name": n1_name if child == n1_id else n2_name,
                        "similarity": round(sim, 4),
                        "relationship": "IS_A"
                    })
        
        return hierarchies

    def _determine_parent_child(
        self, 
        n1_id: str, 
        n2_id: str, 
        n1_name: str, 
        n2_name: str
    ) -> tuple:
        """Determines which node is likely the parent (hypernym) vs child (hyponym)."""
        n1_name_len = len(n1_name) if n1_name else len(n1_id)
        n2_name_len = len(n2_name) if n2_name else len(n2_id)
        
        if n1_name_len <= n2_name_len:
            return (n1_id, n2_id)
        return (n2_id, n1_id)

    def build_taxonomy_tree(self, hierarchies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Builds a hierarchical tree structure from detected relationships."""
        tree = {"nodes": [], "relationships": []}
        
        children_by_parent = defaultdict(list)
        root_nodes = set()
        
        all_node_ids = {n.get('id', f'node_{i}') for i, n in enumerate(self.nodes)}
        
        for h in hierarchies:
            parent = h.get('parent')
            child = h.get('child')
            
            if parent and child:
                children_by_parent[parent].append(child)
                tree["relationships"].append(h)
        
        for node_id in all_node_ids:
            if node_id not in children_by_parent:
                root_nodes.add(node_id)
        
        for root in root_nodes:
            tree["nodes"].append({
                "id": root,
                "name": self._node_map.get(root, {}).get('name', ''),
                "children": children_by_parent.get(root, []),
                "is_root": True
            })
        
        return tree

    def find_concept_clusters(self, threshold: float = 0.7) -> List[List[str]]:
        """Finds clusters of related concepts using transitive similarity."""
        clusters = []
        visited: Set[str] = set()
        
        for i in range(len(self.nodes)):
            n1_id = self.nodes[i].get('id', f'node_{i}')
            
            if n1_id in visited:
                continue
            
            cluster = [n1_id]
            visited.add(n1_id)
            
            for j in range(len(self.nodes)):
                if i == j:
                    continue
                    
                n2_id = self.nodes[j].get('id', f'node_{j}')
                
                if n2_id in visited:
                    continue
                
                sim = self.matrix.get(n1_id, {}).get(n2_id, 0)
                
                if sim >= threshold:
                    cluster.append(n2_id)
                    visited.add(n2_id)
            
            if len(cluster) > 1:
                clusters.append(cluster)
        
        return clusters

    def generate_hierarchy_cypher(self, hierarchies: List[Dict[str, Any]]) -> str:
        """Generates Cypher queries to establish hierarchical links."""
        queries = []
        
        for h in hierarchies:
            parent = h.get('parent', '')
            child = h.get('child', '')
            
            if parent and child:
                query = (
                    f"MATCH (p {{id: '{parent}'}}), (c {{id: '{child}'}}) "
                    f"MERGE (c)-[:IS_A]->(p);"
                )
                queries.append(query)
        
        return "\n".join(queries)

    def generate_cluster_cypher(self, clusters: List[List[str]], rel_type: str = "SAME_CLUSTER") -> str:
        """Generates Cypher queries to link concept clusters."""
        queries = []
        
        for cluster in clusters:
            for i, node_a in enumerate(cluster):
                for node_b in cluster[i+1:]:
                    query = (
                        f"MATCH (a {{id: '{node_a}'}}), (b {{id: '{node_b}'}}) "
                        f"MERGE (a)-[:{rel_type}]->(b);"
                    )
                    queries.append(query)
        
        return "\n".join(queries)

    def generate_taxonomy_report(self) -> Dict[str, Any]:
        """Generates comprehensive taxonomy analysis report."""
        hierarchies = self.detect_hierarchy()
        clusters = self.find_concept_clusters()
        tree = self.build_taxonomy_tree(hierarchies)
        
        return {
            "metadata": {
                "author": "joaquinescalante23",
                "timestamp": datetime.now().isoformat(),
                "total_nodes": len(self.nodes)
            },
            "hierarchies": hierarchies,
            "hierarchy_count": len(hierarchies),
            "clusters": clusters,
            "cluster_count": len(clusters),
            "tree": tree
        }


if __name__ == "__main__":
    nodes = [
        {"id": "Machine_Learning", "name": "Machine Learning"},
        {"id": "Deep_Learning", "name": "Deep Learning"},
        {"id": "Neural_Network", "name": "Neural Network"},
        {"id": "NLP", "name": "Natural Language Processing"},
        {"id": "Computer_Vision", "name": "Computer Vision"}
    ]
    
    matrix = {
        "Machine_Learning": {"Deep_Learning": 0.88, "Neural_Network": 0.85},
        "Deep_Learning": {"Machine_Learning": 0.88, "Neural_Network": 0.92},
        "Neural_Network": {"Deep_Learning": 0.92, "Machine_Learning": 0.85},
        "NLP": {"Machine_Learning": 0.75},
        "Computer_Vision": {"Machine_Learning": 0.70}
    }
    
    builder = TaxonomyBuilder(nodes, matrix)
    import json
    
    print("=== Taxonomy Report ===")
    print(json.dumps(builder.generate_taxonomy_report(), indent=2))
    
    print("\n=== Hierarchy Cypher ===")
    hierarchies = builder.detect_hierarchy()
    print(builder.generate_hierarchy_cypher(hierarchies))
