## Leverage vs Risk Matrix

Every hypothesis gets two scores, not one:

RISK: How bad is it if this hypothesis is wrong?
- HIGH: If wrong, we build entirely the wrong thing
- MEDIUM: If wrong, product needs to be better 
  than existing solution  
- LOW: If wrong, this is a communication or 
  positioning problem

LEVERAGE: How much does being right about this 
change everything else?
- HIGH: Answering this determines whether other 
  hypotheses are worth testing at all. 
  It is a prerequisite, not a feature.
- MEDIUM: Answering this improves one specific 
  workflow or decision.
- LOW: Answering this optimizes something 
  already directionally correct.

Priority rules based on combined score:

HIGH leverage + LOW risk = RUN FIRST
Cheapest, highest-value experiments. Answer 
foundational questions before strategic bets.
Flag with: "PRIORITY: Run this first — low 
cost to test, determines whether other 
hypotheses are measuring the right thing."

HIGH leverage + HIGH risk = RUN SECOND
Big bets. Don't run before foundational 
questions are answered.

LOW leverage + LOW risk = RUN THIRD
Useful optimizations. Don't prioritize over 
foundational or strategic questions.

LOW leverage + HIGH risk = DEPRIORITIZE
High cost, low learning value. Skip unless 
all higher leverage questions are answered.

## Speed to Signal

Before finalizing leverage classification, 
assess how quickly this feature produces 
learnable signal:

HIGH: Results visible in under 2 weeks
MEDIUM: Results visible in 2-4 weeks
LOW: Results visible in over 4 weeks

Speed to Signal Rule:
If a lower DHM option has significantly higher 
speed to signal, flag it as the recommended 
starting point with this note:

"FAST VALIDATION FIRST: Despite lower 
defensibility, [Option X] produces signal 
in [timeframe] vs [Option Y]'s [timeframe]. 
Recommend starting with [X] to validate 
the core mechanism before investing in 
the more defensible solution."

This prevents the system from recommending 
the strategically superior solution when 
the pragmatic minimum viable test has not 
been run yet.
