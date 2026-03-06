---
name: agentic-reasoning-validator
description: Advanced validation suite for agentic reasoning traces and autonomous workflows. Use this skill to (1) Parse and structure agent logs from LangChain, AutoGPT, OpenAI, (2) Detect reasoning loops, circular patterns, tool hallucinations, (3) Evaluate semantic coherence using Shannon entropy and lexical diversity.
---

# Agentic Reasoning Validator (ARV)
**Developed by: [joaquinescalante23](https://github.com/joaquinescalante23)**

Professional-grade validation suite for auditing cognitive processes of autonomous agents.

## Quick Start

### Parse and Audit a Trace:
```bash
python3 cli.py <path_to_log.txt>
```

### With Tool Schema Validation:
```bash
python3 cli.py <path_to_log.txt> --tools get_weather search_flights filter_data
```

### Programmatic Usage:
```python
from scripts.trace_parser import TraceParser
from scripts.semantic_auditor import SemanticAuditor
from scripts.trace_to_mermaid import TraceVisualizer, VisualizationType

# Parse
parser = TraceParser(log_content)
structured = parser.get_structured_trace()

# Analyze
thoughts = [e.get('thought', '') for e in structured['structured_trace']]
auditor = SemanticAuditor(thoughts)
report = auditor.audit_drift()

# Visualize
viz = TraceVisualizer(structured['structured_trace'])
flowchart = viz.generate_mermaid(VisualizationType.FLOWCHART)
```

## Features

| Feature | Description |
|---------|-------------|
| Multi-format parsing | LangChain, AutoGPT, OpenAI, Anthropic, JSON |
| Entropy analysis | Shannon entropy for reasoning complexity |
| Circular detection | N-gram Jaccard similarity |
| Tool hallucination | Schema validation |
| 4 visualization types | Flowchart, Sequence, State, Journey |

## Detected Anti-Patterns

- **Infinite Loop**: Repeated tool calls >3x
- **Circular Reasoning**: N-gram similarity >70%
- **Tool Hallucination**: Undefined tool calls
- **Indecision**: Keywords (again, not sure, verify)
- **Context Drift**: Entropy decreasing over time

## Core Principles

- **Trace-First Debugging**: Never debug an agent by output alone; always analyze the trace
- **Hybrid Validation**: Combine deterministic checks (loops, syntax) with semantic LLM checks
- **Academic Rigor**: Categorize failures using established anti-patterns

## References

- `references/reasoning_patterns.md` - Anti-patterns documentation
- `references/cognitive_architectures.md` - Theoretical foundation
