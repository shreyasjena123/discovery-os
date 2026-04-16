## Input
Raw text: interview transcripts, Reddit threads, 
app reviews, or any unstructured user signal

## Step 1: Bias Detection Layer (runs silently first)
Before generating any output, check the input against 
all 4 bias patterns:

- PROXY PAIN: Is there a stated request masking a deeper frustration?
- WORKAROUND: Has the user already solved this good enough?
- WRONG METRIC: What is the user protecting with current behavior?
- RESEARCH-DECISION GAP: Can I draw a direct line from 
  this signal to a specific product decision?

## Step 2: Generate Output
Only after bias checks complete. Output must include:

1. SIGNALS: specific findings with direct evidence quotes
2. BIAS FLAGS: what the silent layer caught, with evidence
3. WHAT TO ACTUALLY BUILD: a decision + 2 competing 
   approaches tied directly to the evidence

## Step 3: Steel Man the Opposite
After generating the recommendation, ask:
"What would have to be true for this recommendation 
to be wrong?"

Generate 2-3 specific conditions that would invalidate 
the recommendation. Each condition must be:
- Tied to evidence in the input
- Testable with a specific user action or data point
- Phrased as "This recommendation fails if..."

## Output Format
---
SIGNALS FOUND:
[finding] → [direct quote as evidence]

BIAS FLAGS:
[bias type]: [what was detected] → [evidence]

RECOMMENDATION:
The decision to make is [X].
Two ways to solve it:
Option A: [approach] because [evidence]
Option B: [approach] because [evidence]
Lean toward A/B if [specific condition]

STEEL MAN:
- This recommendation fails if [specific condition]
  → Test: [specific action that would reveal this]

RUBRIC SCORE: [auto-score against /evals/process-signals-rubric.md]
---
