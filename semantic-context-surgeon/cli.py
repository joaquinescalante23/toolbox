#!/usr/bin/env python3
"""
Semantic Context Surgeon - CLI
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Command-line interface for context ranking and pruning.
"""

import sys
import json
import argparse
from pathlib import Path

def load_json(path: str):
    """Load JSON data from file."""
    with open(path, 'r') as f:
        return json.load(f)

def rank_command(args):
    """Rank context chunks by relevance."""
    from scripts.ranker import ContextRanker
    
    if args.context:
        data = load_json(args.context)
        chunks = data if isinstance(data, list) else data.get('chunks', [])
    else:
        chunks = []
    
    ranker = ContextRanker(args.query, chunks)
    
    if args.deduplicate:
        results = ranker.rank_and_deduplicate(
            top_k=args.top_k,
            similarity_threshold=args.similarity
        )
    else:
        results = ranker.rank(
            top_k=args.top_k,
            min_score=args.min_score,
            use_position_weight=args.position_weight,
            use_length_weight=args.length_weight
        )
    
    print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {args.output}")
    
    print(f"\nDiversity Score: {ranker.get_diversity_score()}")

def embed_rank_command(args):
    """Rank using embeddings."""
    from scripts.embedding_ranker import EmbeddingRanker
    
    if args.context:
        data = load_json(args.context)
        chunks = data if isinstance(data, list) else data.get('chunks', [])
    else:
        chunks = []
    
    ranker = EmbeddingRanker(args.query, chunks, model_name=args.model)
    
    if args.diversity:
        results = ranker.rank_with_diversity(top_k=args.top_k, diversity_weight=args.diversity_weight)
    else:
        results = ranker.rank(top_k=args.top_k)
    
    print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

def bm25_rank_command(args):
    """Rank using BM25."""
    from scripts.bm25_ranker import BM25Ranker
    
    if args.context:
        data = load_json(args.context)
        chunks = data if isinstance(data, list) else data.get('chunks', [])
    else:
        chunks = []
    
    ranker = BM25Ranker(args.query, chunks)
    results = ranker.rank(top_k=args.top_k)
    
    print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

def expand_command(args):
    """Expand query."""
    from scripts.query_expander import QueryExpander, ContextualQueryExpander
    
    if args.context:
        data = load_json(args.context)
        context_chunks = data if isinstance(data, list) else data.get('chunks', [])
        expander = ContextualQueryExpander(args.query, context_chunks)
    else:
        expander = QueryExpander(args.query)
    
    expanded = expander.expand(
        include_synonyms=not args.no_synonyms,
        include_concepts=not args.no_concepts,
        include_context=not args.no_context
    )
    
    report = expander.get_expansion_report()
    print(json.dumps(report, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)

def optimize_command(args):
    """Optimize context window."""
    from scripts.context_optimizer import ContextWindowOptimizer, PlacementStrategy, AdaptiveWindowOptimizer
    
    if args.context:
        data = load_json(args.context)
        chunks = data if isinstance(data, list) else data.get('chunks', [])
    else:
        chunks = []
    
    if args.auto:
        optimizer = AdaptiveWindowOptimizer(args.max_tokens)
        result = optimizer.optimize_auto(chunks)
    else:
        strategy = PlacementStrategy(args.strategy)
        optimizer = ContextWindowOptimizer(args.max_tokens)
        result = optimizer.optimize(chunks, strategy)
    
    print(json.dumps(result, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)

def chunk_command(args):
    """Handle chunk overlaps."""
    from scripts.chunk_overlap import ChunkOverlapHandler, SmartChunker, SlidingWindowChunker
    
    with open(args.input, 'r') as f:
        text = f.read()
    
    if args.mode == "sentences":
        chunker = SmartChunker(chunk_size=args.chunk_size)
        results = chunker.chunk_by_sentences(text)
    elif args.mode == "paragraphs":
        chunker = SmartChunker(chunk_size=args.chunk_size)
        results = chunker.chunk_by_paragraphs(text)
    elif args.mode == "sliding":
        chunker = SlidingWindowChunker(window_size=args.chunk_size, stride=args.stride)
        results = chunker.chunk(text)
    else:
        handler = ChunkOverlapHandler(overlap_chars=args.overlap)
        results = handler.split_with_overlap(text, args.chunk_size, overlap_type=args.mode)
    
    print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

def prune_command(args):
    """Trim text to fit token budget."""
    from scripts.pruner import TokenBudgetManager, TrimStrategy
    
    with open(args.input, 'r') as f:
        text = f.read()
    
    strategy = TrimStrategy(args.strategy)
    manager = TokenBudgetManager(
        max_tokens=args.max_tokens,
        chars_per_token=args.chars_per_token
    )
    
    if args.info:
        info = manager.get_budget_info(text)
        print(json.dumps(info, indent=2))
        return
    
    if strategy == TrimStrategy.SURGICAL:
        result = manager.surgical_trim(text)
    elif strategy == TrimStrategy.TAIL:
        result = manager.tail_trim(text)
    elif strategy == TrimStrategy.HEAD_AND_TAIL:
        result = manager.head_and_tail_trim(text)
    else:
        result = manager.smart_trim(text, strategy=strategy)
    
    print(result)
    
    if args.output:
        with open(args.output, 'w') as f:
            f.write(result)
        print(f"\nTrimmed text saved to: {args.output}")

def batch_command(args):
    """Trim multiple chunks."""
    from scripts.pruner import TokenBudgetManager, TrimStrategy
    
    data = load_json(args.input)
    chunks = data.get('chunks', data) if isinstance(data, dict) else data
    
    strategy = TrimStrategy(args.strategy)
    manager = TokenBudgetManager(
        max_tokens=args.max_tokens,
        chars_per_token=args.chars_per_token
    )
    
    results = manager.trim_multiple(chunks, strategy=strategy)
    
    print(json.dumps(results, indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(results, f, indent=2)

def main():
    parser = argparse.ArgumentParser(
        description="Semantic Context Surgeon - Context pruning and ranking tools"
    )
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Rank command
    rank_parser = subparsers.add_parser('rank', help='Rank by keyword relevance')
    rank_parser.add_argument('query', help='Query string')
    rank_parser.add_argument('--context', '-c', help='JSON file with context chunks')
    rank_parser.add_argument('--top_k', '-k', type=int, default=5)
    rank_parser.add_argument('--deduplicate', '-d', action='store_true')
    rank_parser.add_argument('--similarity', '-s', type=float, default=0.9)
    rank_parser.add_argument('--position_weight', '-p', type=float, default=0.2)
    rank_parser.add_argument('--length_weight', '-l', type=float, default=0.1)
    rank_parser.add_argument('-o', '--output', help='Output file')
    
    # Embed rank command
    embed_parser = subparsers.add_parser('embed', help='Rank by embeddings')
    embed_parser.add_argument('query', help='Query string')
    embed_parser.add_argument('--context', '-c', help='JSON file with context chunks')
    embed_parser.add_argument('--top_k', '-k', type=int, default=5)
    embed_parser.add_argument('--model', '-m', default='all-MiniLM-L6-v2')
    embed_parser.add_argument('--diversity', action='store_true')
    embed_parser.add_argument('--diversity_weight', type=float, default=0.3)
    embed_parser.add_argument('-o', '--output', help='Output file')
    
    # BM25 rank command
    bm25_parser = subparsers.add_parser('bm25', help='Rank by BM25')
    bm25_parser.add_argument('query', help='Query string')
    bm25_parser.add_argument('--context', '-c', help='JSON file with context chunks')
    bm25_parser.add_argument('--top_k', '-k', type=int, default=5)
    bm25_parser.add_argument('-o', '--output', help='Output file')
    
    # Expand command
    expand_parser = subparsers.add_parser('expand', help='Expand query')
    expand_parser.add_argument('query', help='Query string')
    expand_parser.add_argument('--context', '-c', help='JSON context for expansion')
    expand_parser.add_argument('--no_synonyms', action='store_true')
    expand_parser.add_argument('--no_concepts', action='store_true')
    expand_parser.add_argument('--no_context', action='store_true')
    expand_parser.add_argument('-o', '--output', help='Output file')
    
    # Optimize command
    opt_parser = subparsers.add_parser('optimize', help='Optimize context window')
    opt_parser.add_argument('--context', '-c', help='JSON file with chunks')
    opt_parser.add_argument('--max_tokens', '-t', type=int, default=2000)
    opt_parser.add_argument('--strategy', '-s', choices=['equal_spaced', 'primacy', 'recency', 'pyramid', 'horse', 'focus'], default='horse')
    opt_parser.add_argument('--auto', action='store_true', help='Auto-select best strategy')
    opt_parser.add_argument('-o', '--output', help='Output file')
    
    # Chunk command
    chunk_parser = subparsers.add_parser('chunk', help='Split text into chunks')
    chunk_parser.add_argument('input', help='Input text file')
    chunk_parser.add_argument('--mode', choices=['sentence', 'word', 'char', 'sentences', 'paragraphs', 'sliding'], default='sentence')
    chunk_parser.add_argument('--chunk_size', '-s', type=int, default=500)
    chunk_parser.add_argument('--overlap', type=int, default=50)
    chunk_parser.add_argument('--stride', type=int, default=100)
    chunk_parser.add_argument('-o', '--output', help='Output file')
    
    # Prune command
    prune_parser = subparsers.add_parser('prune', help='Trim text to fit token budget')
    prune_parser.add_argument('input', help='Input text file')
    prune_parser.add_argument('--max_tokens', '-t', type=int, default=1000)
    prune_parser.add_argument('--chars_per_token', type=float, default=4.0)
    prune_parser.add_argument('--strategy', choices=['surgical', 'head', 'tail', 'head_and_tail'], default='head_and_tail')
    prune_parser.add_argument('--info', '-i', action='store_true')
    prune_parser.add_argument('-o', '--output', help='Output file')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Trim multiple chunks')
    batch_parser.add_argument('input', help='JSON input file')
    batch_parser.add_argument('--max_tokens', '-t', type=int, default=1000)
    batch_parser.add_argument('--chars_per_token', type=float, default=4.0)
    batch_parser.add_argument('--strategy', choices=['surgical', 'head', 'tail', 'head_and_tail'], default='head_and_tail')
    batch_parser.add_argument('-o', '--output', help='Output file')
    
    args = parser.parse_args()
    
    commands = {
        'rank': rank_command,
        'embed': embed_rank_command,
        'bm25': bm25_rank_command,
        'expand': expand_command,
        'optimize': optimize_command,
        'chunk': chunk_command,
        'prune': prune_command,
        'batch': batch_command
    }
    
    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
