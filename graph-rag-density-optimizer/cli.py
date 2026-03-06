#!/usr/bin/env python3
"""
Graph-RAG Density Optimizer - CLI
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Command-line interface for Graph-RAG optimization tools.
"""

import sys
import json
import argparse
from pathlib import Path

def load_json(path: str):
    """Load JSON data from file."""
    with open(path, 'r') as f:
        return json.load(f)

def audit_command(args):
    """Run topology audit on graph data."""
    from scripts.audit import TopologyAudit
    
    data = load_json(args.input)
    nodes = data.get('nodes', [])
    edges = data.get('edges', [])
    
    audit = TopologyAudit(nodes, edges)
    report = audit.audit_report()
    
    print(json.dumps(report, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")
    
    if args.generate_queries:
        isolated = audit.identify_isolated_nodes()
        queries = audit.generate_delete_queries(isolated)
        print("\n--- Delete Queries ---")
        print(queries)

def merge_command(args):
    """Run semantic merging on nodes."""
    from scripts.merger import SemanticMerger
    
    data = load_json(args.input)
    nodes = data.get('nodes', [])
    
    merger = SemanticMerger(nodes, args.threshold)
    
    summary = merger.generate_summary_stats()
    print(json.dumps(summary, indent=2))
    
    duplicates = merger.find_duplicates()
    if duplicates:
        print("\n--- Potential Merges ---")
        print(json.dumps(duplicates, indent=2))
        
        if args.generate_queries:
            cypher = merger.generate_cypher_merge(duplicates)
            print("\n--- Cypher Queries ---")
            print(cypher)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump({"summary": summary, "merges": duplicates}, f, indent=2)

def taxonomy_command(args):
    """Build taxonomy hierarchies."""
    from scripts.taxonomy import TaxonomyBuilder
    
    data = load_json(args.input)
    nodes = data.get('nodes', [])
    matrix = data.get('similarity_matrix', {})
    
    builder = TaxonomyBuilder(nodes, matrix)
    report = builder.generate_taxonomy_report()
    
    print(json.dumps(report, indent=2))
    
    if args.generate_queries:
        hierarchies = report.get('hierarchies', [])
        if hierarchies:
            cypher = builder.generate_hierarchy_cypher(hierarchies)
            print("\n--- Hierarchy Cypher ---")
            print(cypher)
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description="Graph-RAG Density Optimizer - Knowledge Graph refinement tools"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Audit command
    audit_parser = subparsers.add_parser('audit', help='Audit graph topology')
    audit_parser.add_argument('input', help='Input JSON file with nodes and edges')
    audit_parser.add_argument('-o', '--output', help='Output report file')
    audit_parser.add_argument('-q', '--generate-queries', action='store_true', help='Generate Cypher queries')
    
    # Merge command
    merge_parser = subparsers.add_parser('merge', help='Semantic node merging')
    merge_parser.add_argument('input', help='Input JSON file with nodes')
    merge_parser.add_argument('-t', '--threshold', type=float, default=0.95, help='Similarity threshold (default: 0.95)')
    merge_parser.add_argument('-o', '--output', help='Output report file')
    merge_parser.add_argument('-q', '--generate-queries', action='store_true', help='Generate Cypher queries')
    
    # Taxonomy command
    taxonomy_parser = subparsers.add_parser('taxonomy', help='Build taxonomy hierarchies')
    taxonomy_parser.add_argument('input', help='Input JSON file with nodes and similarity matrix')
    taxonomy_parser.add_argument('-o', '--output', help='Output report file')
    taxonomy_parser.add_argument('-q', '--generate-queries', action='store_true', help='Generate Cypher queries')
    
    args = parser.parse_args()
    
    if args.command == 'audit':
        audit_command(args)
    elif args.command == 'merge':
        merge_command(args)
    elif args.command == 'taxonomy':
        taxonomy_command(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
