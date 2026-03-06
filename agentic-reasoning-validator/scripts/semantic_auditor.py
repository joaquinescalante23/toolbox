"""
Agentic Reasoning Validator - Semantic Auditor
Developed by: joaquinescalante23 (https://github.com/joaquinescalante23)
License: MIT
Description: Advanced semantic analysis of agent reasoning. Detects "Reasoning Drift", 
             "Circular Thoughts", "Indecision Patterns", and "Tool Hallucinations" 
             using multiple linguistic and statistical metrics.
"""

from typing import List, Dict, Any, Optional
from collections import Counter
import math
import re
from datetime import datetime
import json


class SemanticAuditor:
    """Advanced semantic auditor for agent reasoning traces."""
    
    def __init__(self, thoughts: List[str], tool_schema: Optional[List[str]] = None):
        self.thoughts = thoughts
        self.tool_schema = tool_schema or []

    def calculate_shannon_entropy(self, text: str) -> float:
        """Calculate Shannon entropy to detect repetitive/robotic thinking."""
        if not text or not text.strip():
            return 0.0
        words = text.lower().split()
        if not words:
            return 0.0
        word_counts = Counter(words)
        total = len(words)
        probs = [count / total for count in word_counts.values()]
        entropy = -sum(p * math.log2(p) for p in probs if p > 0)
        return round(entropy, 4)

    def calculate_lexical_diversity(self, text: str) -> float:
        """Calculate Type-Token Ratio (TTR) - measure of vocabulary richness."""
        if not text or not text.strip():
            return 0.0
        words = text.lower().split()
        if not words:
            return 0.0
        unique_words = len(set(words))
        ttr = unique_words / len(words)
        return round(ttr, 4)

    def detect_circular_patterns(self, window_size: int = 3) -> List[Dict[str, Any]]:
        """Detect circular reasoning using n-gram similarity."""
        if len(self.thoughts) < window_size:
            return []
        
        circular_patterns = []
        for i in range(len(self.thoughts) - window_size + 1):
            window = self.thoughts[i:i + window_size]
            ngrams = self._get_ngrams(window[0], 3)
            
            similarity_scores = []
            for j in range(1, window_size):
                other_ngrams = self._get_ngrams(window[j], 3)
                similarity = self._jaccard_similarity(ngrams, other_ngrams)
                similarity_scores.append(similarity)
            
            avg_similarity = sum(similarity_scores) / len(similarity_scores)
            
            if avg_similarity > 0.7:
                circular_patterns.append({
                    "start_step": i,
                    "end_step": i + window_size - 1,
                    "avg_similarity": round(avg_similarity, 4),
                    "severity": "HIGH" if avg_similarity > 0.85 else "MEDIUM"
                })
        
        return circular_patterns

    def _get_ngrams(self, text: str, n: int) -> set:
        """Extract n-grams from text."""
        words = text.lower().split()
        if len(words) < n:
            return set()
        return set(tuple(words[i:i+n]) for i in range(len(words) - n + 1))

    def _jaccard_similarity(self, set1: set, set2: set) -> float:
        """Calculate Jaccard similarity between two sets."""
        if not set1 or not set2:
            return 0.0
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0

    def detect_indecision_patterns(self) -> List[Dict[str, Any]]:
        """Detect indecision patterns (repeated 'checking again', 'not sure', etc.)."""
        indecision_keywords = [
            r'\bagain\b', r'\bnot sure\b', r'\buncertain\b', r'\bdoubt\b',
            r'\bmaybe\b', r'\bperhaps\b', r'\bre-check\b', r'\bverify\b',
            r'\bdouble-check\b', r'\bvalidate\b', r'\bjust to be sure\b'
        ]
        
        indecision_patterns = []
        for i, thought in enumerate(self.thoughts):
            matches = []
            for pattern in indecision_keywords:
                if re.search(pattern, thought.lower()):
                    matches.append(pattern)
            
            if matches:
                indecision_patterns.append({
                    "step": i,
                    "matched_patterns": matches,
                    "count": len(matches)
                })
        
        return indecision_patterns

    def calculate_reasoning_progression(self) -> Dict[str, Any]:
        """Analyze if reasoning is progressing or regressing."""
        if len(self.thoughts) < 2:
            return {"progression": "INSUFFICIENT_DATA", "trend": []}
        
        entropies = [self.calculate_shannon_entropy(t) for t in self.thoughts]
        diversities = [self.calculate_lexical_diversity(t) for t in self.thoughts]
        
        trend = []
        for i in range(1, len(entropies)):
            entropy_change = entropies[i] - entropies[i-1]
            diversity_change = diversities[i] - diversities[i-1]
            
            if entropy_change < -0.5 and diversity_change < -0.1:
                trend.append("REGRESSING")
            elif entropy_change > 0.5 or diversity_change > 0.1:
                trend.append("PROGRESSING")
            else:
                trend.append("STABLE")
        
        return {
            "progression": max(set(trend), key=trend.count) if trend else "STABLE",
            "trend": trend,
            "avg_entropy": round(sum(entropies) / len(entropies), 4),
            "avg_diversity": round(sum(diversities) / len(diversities), 4)
        }

    def detect_tool_hallucinations(self, tool_calls: List[str]) -> List[Dict[str, Any]]:
        """Detect tool hallucinations by comparing against provided tool schema."""
        if not self.tool_schema:
            return []
        
        hallucinations = []
        for i, tool_call in enumerate(tool_calls):
            tool_name_match = re.match(r'(\w+)\s*\(', tool_call)
            if tool_name_match:
                tool_name = tool_name_match.group(1)
                if tool_name not in self.tool_schema:
                    hallucinations.append({
                        "step": i,
                        "attempted_tool": tool_name,
                        "severity": "HIGH",
                        "message": f"Tool '{tool_name}' not found in provided schema"
                    })
        
        return hallucinations

    def audit_drift(self) -> Dict[str, Any]:
        """Main audit method - analyzes all aspects of reasoning."""
        analysis_results = {
            "metadata": {
                "author": "joaquinescalante23",
                "version": "2.0.0-PRO",
                "timestamp": datetime.now().isoformat(),
                "total_thoughts": len(self.thoughts)
            },
            "entropy_analysis": [],
            "circular_patterns": self.detect_circular_patterns(),
            "indecision_patterns": self.detect_indecision_patterns(),
            "progression": self.calculate_reasoning_progression(),
            "overall_health": "UNKNOWN",
            "health_score": 0
        }
        
        for i, thought in enumerate(self.thoughts):
            entropy = self.calculate_shannon_entropy(thought)
            diversity = self.calculate_lexical_diversity(thought)
            
            status = "HEALTHY"
            if entropy < 2.0:
                status = "CRITICAL_LOOP"
            elif entropy < 3.0:
                status = "POTENTIAL_LOOP"
            elif diversity < 0.3:
                status = "LOW_VARIETY"
            
            analysis_results["entropy_analysis"].append({
                "step": i,
                "entropy": entropy,
                "diversity": diversity,
                "word_count": len(thought.split()),
                "status": status
            })
        
        health_scores = {
            "CRITICAL_LOOP": 0,
            "POTENTIAL_LOOP": 25,
            "LOW_VARIETY": 50,
            "HEALTHY": 100,
            "STABLE": 75
        }
        
        statuses = [a["status"] for a in analysis_results["entropy_analysis"]]
        avg_health = sum(health_scores.get(s, 75) for s in statuses) / len(statuses)
        
        if analysis_results["circular_patterns"]:
            avg_health -= 20 * len(analysis_results["circular_patterns"])
        
        if analysis_results["indecision_patterns"]:
            avg_health -= 10 * len(analysis_results["indecision_patterns"])
        
        if avg_health >= 80:
            analysis_results["overall_health"] = "EXCELLENT"
        elif avg_health >= 60:
            analysis_results["overall_health"] = "GOOD"
        elif avg_health >= 40:
            analysis_results["overall_health"] = "NEEDS_ATTENTION"
        else:
            analysis_results["overall_health"] = "CRITICAL"
        
        analysis_results["health_score"] = max(0, round(avg_health, 2))
        
        return analysis_results

    def generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        audit = self.audit_drift()
        recommendations = []
        
        if audit["circular_patterns"]:
            recommendations.append(
                f"Detected {len(audit['circular_patterns'])} circular reasoning pattern(s). "
                "Consider adding a 'max_iterations' limit or forcing a reasoning pivot."
            )
        
        if audit["indecision_patterns"]:
            recommendations.append(
                f"Found {len(audit['indecision_patterns'])} indecision markers. "
                "System prompt may need clearer decision criteria."
            )
        
        progression = audit["progression"]
        if progression.get("progression") == "REGRESSING":
            recommendations.append(
                "Reasoning is regressing (losing complexity). "
                "Consider adding intermediate goal checkpoints."
            )
        
        if audit["health_score"] < 50:
            recommendations.append(
                "Overall health score is critical. Review agent architecture and prompting strategy."
            )
        
        if not recommendations:
            recommendations.append("No significant issues detected. Agent reasoning appears healthy.")
        
        return recommendations


if __name__ == "__main__":
    thoughts = [
        "I need to check the data again because I am not sure.",
        "Checking data again to be sure of the result.",
        "Checking data again because I am not sure.",
        "Let me verify the calculation one more time to be certain.",
        "The data looks consistent with previous observations."
    ]
    
    auditor = SemanticAuditor(thoughts)
    audit_result = auditor.audit_drift()
    
    print(json.dumps(audit_result, indent=2))
    print("\nRecommendations:")
    for rec in auditor.generate_recommendations():
        print(f"  - {rec}")
