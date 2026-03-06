"""
Graph-RAG Density Optimizer - Topology Audit
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Audit tool for Graph-RAG Topologies. Identifies low-value 'noise' nodes 
             using connectivity analysis (Degree Centrality, Betweenness).
"""

import math
from typing import List, Dict, Any, Optional, Set
from collections import defaultdict
from datetime import datetime


class TopologyAudit:
    """Professional topology auditor for Knowledge Graphs."""
    
    def __init__(self, nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]):
        self.nodes = nodes
        self.edges = edges
        self._node_map = {node.get('id', f'node_{i}'): node for i, node in enumerate(nodes)}

    def calculate_node_degrees(self) -> Dict[str, int]:
        """Calculates the degree (number of connections) for each node."""
        degrees = {node.get('id', f'node_{i}'): 0 for i, node in enumerate(self.nodes)}
        
        for edge in self.edges:
            source = edge.get('source') or edge.get('from') or edge.get('start')
            target = edge.get('target') or edge.get('to') or edge.get('end')
            
            if source and source in degrees:
                degrees[source] += 1
            if target and target in degrees:
                degrees[target] += 1
        
        return degrees

    def calculate_in_out_degrees(self) -> Dict[str, Dict[str, int]]:
        """Calculates in-degree and out-degree for directed graphs."""
        in_degrees = {node.get('id', f'node_{i}'): 0 for i, node in enumerate(self.nodes)}
        out_degrees = {node.get('id', f'node_{i}'): 0 for i, node in enumerate(self.nodes)}
        
        for edge in self.edges:
            source = edge.get('source') or edge.get('from') or edge.get('start')
            target = edge.get('target') or edge.get('to') or edge.get('end')
            
            if source and source in out_degrees:
                out_degrees[source] += 1
            if target and target in in_degrees:
                in_degrees[target] += 1
        
        return {"in": in_degrees, "out": out_degrees}

    def identify_isolated_nodes(self, degree_threshold: int = 1) -> List[Dict[str, Any]]:
        """Identifies nodes with very low connectivity (potential noise)."""
        degrees = self.calculate_node_degrees()
        
        isolated = []
        for node_id, deg in degrees.items():
            if deg <= degree_threshold:
                node_data = self._node_map.get(node_id, {})
                isolated.append({
                    "id": node_id,
                    "name": node_data.get('name', ''),
                    "degree": deg,
                    "reason": "isolated" if deg == 0 else "low_connectivity"
                })
        
        return isolated

    def identify_hub_nodes(self, degree_threshold: int = 10) -> List[Dict[str, Any]]:
        """Identifies highly connected hub nodes."""
        degrees = self.calculate_node_degrees()
        
        hubs = []
        for node_id, deg in degrees.items():
            if deg >= degree_threshold:
                node_data = self._node_map.get(node_id, {})
                hubs.append({
                    "id": node_id,
                    "name": node_data.get('name', ''),
                    "degree": deg,
                    "role": "hub"
                })
        
        return hubs

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """Approximate betweenness centrality for each node."""
        degrees = self.calculate_node_degrees()
        
        betweenness = {node_id: 0.0 for node_id in degrees.keys()}
        
        for node_id in degrees:
            if degrees[node_id] == 0:
                continue
            
            paths_through = 0
            total_paths = 0
            
            for edge in self.edges:
                source = edge.get('source') or edge.get('from') or edge.get('start')
                target = edge.get('target') or edge.get('to') or edge.get('end')
                
                if (source and target) and (node_id in [source, target]):
                    total_paths += 1
                    if source == node_id or target == node_id:
                        paths_through += 1
            
            if total_paths > 0:
                betweenness[node_id] = paths_through / total_paths
        
        return betweenness

    def find_bridge_nodes(self) -> List[Dict[str, Any]]:
        """Identifies nodes that act as bridges between clusters."""
        betweenness = self.calculate_betweenness_centrality()
        degrees = self.calculate_node_degrees()
        
        bridges = []
        for node_id, bc in betweenness.items():
            if bc > 0.1 and degrees.get(node_id, 0) <= 3:
                node_data = self._node_map.get(node_id, {})
                bridges.append({
                    "id": node_id,
                    "name": node_data.get('name', ''),
                    "betweenness": round(bc, 4),
                    "degree": degrees.get(node_id, 0),
                    "role": "bridge"
                })
        
        return bridges

    def generate_delete_queries(self, isolated_nodes: List[Dict]) -> str:
        """Generates Cypher DELETE queries for isolated nodes."""
        queries = []
        for node in isolated_nodes:
            node_id = node.get('id', '')
            if node_id:
                queries.append(f"MATCH (n {{id: '{node_id}'}}) DETACH DELETE n;")
        return "\n".join(queries)

    def audit_report(self) -> Dict[str, Any]:
        """Generates a professional report on the graph's health."""
        degrees = self.calculate_node_degrees()
        isolated = self.identify_isolated_nodes()
        hubs = self.identify_hub_nodes()
        bridges = self.find_bridge_nodes()
        
        total_nodes = len(self.nodes)
        total_edges = len(self.edges)
        noise_ratio = len(isolated) / total_nodes if total_nodes > 0 else 0
        
        avg_degree = sum(degrees.values()) / total_nodes if total_nodes > 0 else 0
        
        recommendations = []
        
        if len(isolated) > 0:
            recommendations.append(
                f"Consider deleting {len(isolated)} isolated nodes with degree <= 1 to optimize RAG pathfinding."
            )
        
        if noise_ratio > 0.3:
            recommendations.append(
                f"High noise ratio ({noise_ratio:.0%}). Review ingestion process for disconnected content."
            )
        
        if len(hubs) > 0:
            recommendations.append(
                f"Found {len(hubs)} hub nodes. Ensure they have proper indexing for query performance."
            )
        
        if bridges:
            recommendations.append(
                f"Found {len(bridges)} bridge nodes. These are critical for graph connectivity."
            )
        
        if not recommendations:
            recommendations.append("Topology is healthy and dense.")
        
        return {
            "metadata": {
                "author": "joaquinescalante23",
                "timestamp": datetime.now().isoformat(),
                "total_nodes": total_nodes,
                "total_edges": total_edges
            },
            "metrics": {
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "isolated_nodes": isolated,
                "isolated_count": len(isolated),
                "hub_nodes": hubs,
                "bridge_nodes": bridges,
                "graph_noise_ratio": round(noise_ratio, 4),
                "average_degree": round(avg_degree, 4),
                "degree_distribution": {
                    "min": min(degrees.values()) if degrees else 0,
                    "max": max(degrees.values()) if degrees else 0,
                    "median": sorted(degrees.values())[len(degrees)//2] if degrees else 0
                }
            },
            "recommendations": recommendations
        }


if __name__ == "__main__":
    nodes = [
        {"id": "A", "name": "AI"},
        {"id": "B", "name": "Machine Learning"},
        {"id": "C", "name": "Deep Learning"},
        {"id": "D", "name": "Neural Network"},
        {"id": "E", "name": "Isolated Node"}
    ]
    edges = [
        {"source": "A", "target": "B"},
        {"source": "B", "target": "C"},
        {"source": "C", "target": "D"}
    ]
    
    audit = TopologyAudit(nodes, edges)
    import json
    print(json.dumps(audit.audit_report(), indent=2))
