# The Art of Context Surgery: Principles of Semantic Pruning
**Author: [joaquinescalante23](https://github.com/joaquinescalante23)**

## 1. The Lost in the Middle Phenomenon
Empirical research shows that LLMs lose accuracy when the context window is bloated with irrelevant data, especially when the crucial information is placed in the middle of the prompt.
- **The Solution:** Semantic Re-ranking. By moving high-relevance chunks to the top and bottom of the prompt (the "Primacy" and "Recency" positions), we maximize model attention.

## 2. Token Budgeting as an Architectural Constraint
Tokens are not just a cost; they are a constraint on the model's "working memory". 
- **The Axiom:** "Every irrelevant token is a tax on the model's reasoning capacity."
- **The Method:** ARV uses a budget-first approach to ensure only the most dense information is transmitted.

## 3. Sentence-Aware Truncation
Breaking a sentence mid-way introduces "Structural Hallucination", where the model tries to complete a thought that was never there.
- **The Method:** Our Token Budget Manager always terminates at the last valid syntactic boundary.
