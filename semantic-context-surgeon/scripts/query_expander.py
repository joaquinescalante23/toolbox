"""
Semantic Context Surgeon - Query Expander
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Query expansion for improved RAG retrieval. Uses synonyms, 
             concept expansion, and contextual suggestions.
"""

import re
from typing import List, Dict, Any, Set, Optional, Tuple
from collections import defaultdict
import json


class QueryExpander:
    """Query expansion for better retrieval."""
    
    def __init__(self, query: str):
        self.original_query = query
        self.expanded_terms: Set[str] = set()
        self.synonyms = self._load_default_synonyms()
        self.concepts = self._load_default_concepts()
    
    def _load_default_synonyms(self) -> Dict[str, List[str]]:
        """Load default synonym dictionary."""
        return {
            'ai': ['artificial intelligence', 'machine intelligence'],
            'ml': ['machine learning', 'statistical learning'],
            'dl': ['deep learning', 'neural networks'],
            'nlp': ['natural language processing', 'computational linguistics'],
            'cv': ['computer vision', 'image recognition'],
            'db': ['database', 'data store'],
            'rag': ['retrieval augmented generation', 'augmented generation'],
            'kg': ['knowledge graph', 'semantic graph'],
            'llm': ['large language model', 'language model'],
            'optimize': ['improve', 'enhance', 'tune', 'performance'],
            'fast': ['quick', 'rapid', 'speedy'],
            'best': ['optimal', 'top', 'ideal'],
            'build': ['create', 'develop', 'construct'],
            'find': ['search', 'discover', 'locate'],
            'fix': ['resolve', 'solve', 'repair'],
            'learn': ['understand', 'study', 'master'],
            'data': ['information', 'dataset', 'records'],
            'query': ['search', 'request', 'ask'],
            'node': ['vertex', 'entity', 'point'],
            'edge': ['relationship', 'link', 'connection'],
        }
    
    def _load_default_concepts(self) -> Dict[str, List[str]]:
        """Load default concept expansions."""
        return {
            'neo4j': ['graph database', 'cypher', 'property graph', 'graphdb'],
            'python': ['py', 'python3', 'programming language'],
            'javascript': ['js', 'nodejs', 'node'],
            'api': ['endpoint', 'service', 'interface'],
            'cloud': ['aws', 'azure', 'gcp', 'hosted'],
            'search': ['retrieve', 'find', 'query', 'lookup'],
            'embeddings': ['vectors', 'embeddings', 'semantic vectors'],
            'indexing': ['index', 'lookup table', 'hash map'],
            'caching': ['cache', 'memoization', 'store'],
        }
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        return [t for t in text.split() if len(t) > 1]
    
    def expand_by_synonyms(self) -> Set[str]:
        """Expand query using synonyms."""
        terms = self._tokenize(self.original_query)
        expanded = set()
        
        for term in terms:
            if term in self.synonyms:
                expanded.update(self.synonyms[term])
            for key, synonyms in self.synonyms.items():
                if term in synonyms:
                    expanded.add(key)
                    expanded.update(synonyms)
        
        return expanded
    
    def expand_by_concepts(self) -> Set[str]:
        """Expand query using concept expansion."""
        terms = self._tokenize(self.original_query)
        expanded = set()
        
        for term in terms:
            if term in self.concepts:
                expanded.update(self.concepts[term])
        
        return expanded
    
    def expand(self, include_synonyms: bool = True, include_concepts: bool = True) -> str:
        """Expand query with synonyms and/or concepts."""
        expanded = set(self._tokenize(self.original_query))
        
        if include_synonyms:
            expanded.update(self.expand_by_synonyms())
        
        if include_concepts:
            expanded.update(self.expand_by_concepts())
        
        self.expanded_terms = expanded
        return ' '.join(sorted(expanded))
    
    def get_expansion_report(self) -> Dict[str, Any]:
        """Get detailed expansion report."""
        synonyms = self.expand_by_synonyms()
        concepts = self.expand_by_concepts()
        
        return {
            'original_query': self.original_query,
            'expanded_query': ' '.join(sorted(self.expanded_terms)),
            'synonyms_added': list(synonyms),
            'concepts_added': list(concepts),
            'total_expansions': len(self.expanded_terms),
            'expansion_ratio': len(self.expanded_terms) / max(1, len(self._tokenize(self.original_query)))
        }


class ContextualQueryExpander(QueryExpander):
    """Query expander that considers context from chunks."""
    
    def __init__(self, query: str, context_chunks: Optional[List[Dict[str, Any]]] = None):
        super().__init__(query)
        self.context_chunks = context_chunks or []
        self.corpus_terms = self._extract_corpus_terms()
    
    def _extract_corpus_terms(self) -> Set[str]:
        """Extract all terms from context chunks."""
        terms = set()
        for chunk in self.context_chunks:
            text = chunk.get('text', '')
            terms.update(self._tokenize(text))
        return terms
    
    def expand_from_context(self) -> Set[str]:
        """Expand query using terms found in context."""
        query_terms = set(self._tokenize(self.original_query))
        context_expansions = set()
        
        for corpus_term in self.corpus_terms:
            for query_term in query_terms:
                if query_term in corpus_term or corpus_term in query_term:
                    if corpus_term != query_term:
                        context_expansions.add(corpus_term)
        
        return context_expansions
    
    def expand(self, include_synonyms: bool = True, include_concepts: bool = True, include_context: bool = True) -> str:
        """Expand query including context-based terms."""
        expanded = set(self._tokenize(self.original_query))
        
        if include_synonyms:
            expanded.update(self.expand_by_synonyms())
        
        if include_concepts:
            expanded.update(self.expand_by_concepts())
        
        if include_context and self.context_chunks:
            expanded.update(self.expand_from_context())
        
        self.expanded_terms = expanded
        return ' '.join(sorted(expanded))


class BoosedQueryExpander(QueryExpander):
    """Query expander that boosts important terms."""
    
    def __init__(self, query: str, boost_terms: Optional[List[str]] = None):
        super().__init__(query)
        self.boost_terms = set(boost_terms or [])
    
    def expand_with_boost(self, boost_factor: float = 2.0) -> Dict[str, Any]:
        """Expand query and identify boosted terms."""
        expanded = self.expand()
        boosted = []
        
        for term in self.expanded_terms:
            if term in self.boost_terms or any(t in term for t in self.boost_terms):
                boosted.append(f"{term}^{boost_factor}")
            else:
                boosted.append(term)
        
        return {
            'expanded_query': ' '.join(boosted),
            'boosted_terms': [t for t in boosted if '^' in t],
            'all_terms': boosted
        }


if __name__ == "__main__":
    query = "Neo4j optimization for RAG"
    
    print("=== Basic Expansion ===")
    expander = QueryExpander(query)
    expanded = expander.expand()
    print(f"Original: {query}")
    print(f"Expanded: {expanded}")
    print(f"Report: {json.dumps(expander.get_expansion_report(), indent=2)}")
    
    print("\n=== Contextual Expansion ===")
    chunks = [
        {"text": "Neo4j graph database optimization techniques."},
        {"text": "RAG retrieval augmented generation methods."},
    ]
    contextual = ContextualQueryExpander(query, chunks)
    expanded = contextual.expand()
    print(f"Expanded: {expanded}")
    
    print("\n=== Boosted Expansion ===")
    booster = BoosedQueryExpander(query, boost_terms=["neo4j", "optimization"])
    result = booster.expand_with_boost()
    print(f"Boosted: {result['expanded_query']}")
    print(f"Boosted terms: {result['boosted_terms']}")
