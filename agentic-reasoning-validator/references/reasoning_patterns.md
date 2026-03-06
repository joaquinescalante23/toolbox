# Reasoning Patterns & Anti-Patterns for AI Agents
**Author: [joaquinescalante23](https://github.com/joaquinescalante23)**

This reference document outlines the cognitive structures required for reliable agentic behavior.

## 🚫 Common Anti-Patterns

### 1. The Infinite Loop (The "Hamster Wheel")
The agent repeats the same tool call with the same parameters despite receiving the same error or result.
*   **Detection:** Look for >3 identical tool calls in the trace.
*   **Fix:** Force a "Reasoning Pivot" in the system prompt.

### 2. Tool Hallucination
The agent attempts to call a function that was not provided in the tool definitions.
*   **Detection:** Cross-reference tool calls against the `tools_schema`.

### 3. Context Drift
The agent loses track of the original objective after multiple tool-call iterations.
*   **Detection:** Use a "Judge LLM" to compare current step N with the initial user query.

## ✅ Best Practices (The "Gold Standard")

### 1. Chain-of-Thought (CoT) Verification
Every action MUST be preceded by a "Thought" block explaining the rationale.

### 2. Self-Correction Steps
The agent should explicitly check its own output before finalizing the response.
