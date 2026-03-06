# Agentic Reasoning Validator (ARV)
**Advanced Observability and Semantic Auditing for Autonomous Agents**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Author: joaquinescalante23](https://img.shields.io/badge/Author-joaquinescalante23-blue.svg)](https://github.com/joaquinescalante23)

## Overview

**ARV** is a professional-grade validation suite designed for developers building complex agentic systems. Unlike basic log parsers, ARV uses **Information Entropy (Shannon Entropy)**, **N-gram Similarity Analysis**, and **State-Space Visualization** to detect cognitive failure modes in LLM agents.

### Key Features

| Feature | Description |
|---------|-------------|
| **Multi-Format Parsing** | Auto-detects and parses traces from LangChain, AutoGPT, OpenAI Assistants, Anthropic, and custom formats |
| **Semantic Entropy Audit** | Detect robotic thinking and circular reasoning using Shannon entropy and lexical diversity |
| **Circular Pattern Detection** | Uses Jaccard similarity on n-grams to find repetitive thought patterns |
| **Tool Hallucination Detection** | Validates tool calls against a provided schema |
| **4 Visualization Types** | Flowchart, Sequence, State, and Journey diagrams in Mermaid.js |

## Installation

```bash
git clone https://github.com/joaquinescalante23/agentic-reasoning-validator.git
cd agentic-reasoning-validator

# Optional: Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (if any)
# pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```bash
python3 cli.py samples/agent_log.txt
```

### With Tool Schema Validation

```bash
python3 cli.py samples/agent_log.txt --tools get_weather search_flights filter_data
```

### Custom Output

```bash
python3 cli.py samples/agent_log.txt -o my_audit_report.json
```

### Skip Visualization

```bash
python3 cli.py samples/agent_log.txt --no-viz
```

## Output

The CLI generates an `audit_report.json` with:

```json
{
  "metadata": {
    "author": "joaquinescalante23",
    "version": "2.0.0-PRO",
    "source_file": "samples/agent_log.txt"
  },
  "parsing": {
    "detected_format": "autogpt",
    "metadata": {...},
    "loops_detected": {...}
  },
  "audit": {
    "health_score": 85,
    "overall_health": "EXCELLENT",
    "circular_patterns": [...],
    "indecision_patterns": [...],
    "progression": {...}
  },
  "recommendations": [...],
  "visualization": {
    "flowchart": "...",
    "sequence": "...",
    "state": "...",
    "journey": "..."
  }
}
```

## Detected Anti-Patterns

ARV automatically detects these cognitive failure modes:

| Anti-Pattern | Detection Method | Severity |
|--------------|-------------------|----------|
| **Infinite Loop** | Repeated identical tool calls (>3x) | CRITICAL |
| **Circular Reasoning** | High n-gram similarity (>70%) | HIGH |
| **Tool Hallucination** | Undefined tool in schema | CRITICAL |
| **Indecision** | Keywords: "again", "not sure", "verify" | MEDIUM |
| **Context Drift** | Entropy decreasing over time | HIGH |

## Visualization

Copy the generated Mermaid code to [Mermaid Live Editor](https://mermaid.live/) to visualize:

- **Flowchart**: Agent's reasoning path with health indicators
- **Sequence**: Tool interactions and data flow
- **State**: State machine of agent's cognitive states
- **Journey**: Cognitive complexity over time

## Architecture

```
agentic-reasoning-validator/
├── cli.py                      # Main CLI orchestrator
├── scripts/
│   ├── trace_parser.py         # Multi-format trace parser
│   ├── semantic_auditor.py     # Entropy & pattern analysis
│   └── trace_to_mermaid.py    # Visualization generator
├── references/
│   ├── reasoning_patterns.md  # Anti-patterns documentation
│   └── cognitive_architectures.md
├── samples/
│   └── agent_log.txt          # Sample trace for testing
└── assets/
    └── eval_prompts/           # Judge LLM prompts
```

## Theoretical Foundation

This project is based on research in:
- **Information Theory**: Shannon entropy for measuring thought complexity
- **Linguistics**: Type-Token Ratio (TTR) for lexical diversity
- **Set Theory**: Jaccard similarity for pattern matching

See `references/cognitive_architectures.md` for detailed theory.

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

**Joaquín Escalante** - [@joaquinescalante23](https://github.com/joaquinescalante23)

Built for the next generation of Agentic Systems.
