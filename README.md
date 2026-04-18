# PM Discovery OS

**Claude answers the question you asked. This system answers the question you should have asked.**

A CLI and web AI system that runs silent bias detection before every output, forces a full signals to hypotheses to experiments loop, and catches the synthesis failures that kill products before they happen.


---

## The Problem

I kept watching good PMs do great research and still ship the wrong thing.

Not because they were bad at research. Because the synthesis was off. The signal was there in the data, buried in a user quote or a usage pattern, and nobody connected it to the actual product decision.

I noticed this on my own project first. I was building Compass, a compliance tool for school counselors, and I had 200 signups and positive feedback and I was still building the wrong thing. The real job wasn't compliance. It was caseload prioritization. The signal was in my own interview notes. I just didn't see it.

That's what this system is trying to fix. Not replace PM judgment. Just catch the patterns that are easy to miss when you're deep in your own product.

It won't always get it right. But it asks questions that are easy to skip when you're moving fast.

---

## What Makes This Different From Just Asking Claude

| | Raw Claude | PM Discovery OS |
|---|---|---|
| Bias detection | You have to ask | Runs silently before every output |
| Steel Man | Skipped unless you prompt it | Required on every recommendation |
| Fixability check | Never asked | Runs before every recommendation |
| Constraint awareness | Ignores what you can't do | Two tiers: executable now vs. beyond constraints |
| Research memory | Starts fresh every session | Compounds across sessions automatically |
| Framework application | Apply what you know to ask | JTBD, Growth Loops, 7 Powers fire on every run |
| Abandonment signal | Never surfaces it | Flags when optimizing is the wrong move entirely |

The system doesn't answer the question you asked. It answers the question you should have asked. That's the whole point.

---

![PM Discovery OS in action](demo.gif)

## Proof It Works

Six real companies. Raw founding inputs or pre-pivot signals. No post-mortem language. No hints about what went wrong.

---

### Nabla -- AI Healthcare Platform

**Input:** Doctor interviews and usage logs from before the pivot. Documentation never mentioned as the job.

**The buried signal:** Usage logs showed doctors returned to the platform specifically after patient-heavy days. Three interview quotes pointed at documentation without naming it directly: "By the time I sit down to do notes it's already 7pm." "My biggest problem is the pile of notes waiting for me at the end of every shift." "It took longer than just writing it myself." The system connected behavioral data to interview signal across two separate sources without being told they were related.

**What the system caught:**
- `PROXY_PAIN` -- Doctors are requesting features but the real job is: help me reclaim 60-90 minutes per day so I'm not doing clinical work until 11pm
- `WORKAROUND` -- Hospital EHR, iMessage, existing video setup are all entrenched because they already live inside the cognitive flow of a back-to-back patient day. Switching cost is invisible until it's a 7pm decision between learning a new system or going home
- Signal 5 (derived, not stated): "Users who return after patient-heavy days -- this is your JTBD in behavioral form. The platform is being hired, weakly and intermittently, to recover from high-volume clinical days. Not to manage ongoing workflows."
- Recommendation: Stop building features. Collapse to AI note generation. Validate with a 5-field structured input flow in 10 days before full rebuild.

**What actually happened:** Nabla killed 80% of the product and focused solely on AI medical documentation. ARR 5x in 6 months. 85,000 clinicians today.

**Honest note:** The documentation pain was visible in three quotes. What was genuinely buried was the behavioral pattern in usage logs. The system's value here was connecting interview signal to behavioral data across two sources that humans read separately and rarely put together. It also recommended a cheaper validation path than what Nabla actually took.

---

### Compass -- My Own Project

**Input:** Pre-pivot inputs from when I thought I was building a time-tracking compliance tool for school counselors. Fed to the system before I knew I was wrong.

**What the system caught:**
- `PROXY_PAIN` -- Counselors aren't complaining about logging. They're complaining about caseload prioritization. Which of 500 students needs help today.
- `WRONG_METRIC` -- 200 signups in 48 hours measures acquisition interest, not retention or daily habit formation
- `WORKAROUND` -- Color-coded spreadsheets are already functional. The product needs to be meaningfully better, not marginally better
- Kill condition: mandated SIS systems may already own the caseload layer. This was never explicitly tested.
- Recommendation: Build a daily caseload management layer. Make compliance a byproduct of daily workflow, not the primary job.

**What actually happened:** This is the exact pivot I made after months of counselor research. The system re-derived it from pre-pivot inputs in one run. Including a kill condition I had never explicitly identified.

---

### Lotus -- YC S22

**Input:** Founding inputs. #1 Product Hunt. International GitHub contributors. MIT license. Two founders. $500K raised.

**What the system caught:**
- `WRONG_METRIC` -- Developer community traction and commercial traction are different signals. GitHub stars don't predict willingness to pay.
- `RESEARCH_DECISION_GAP` -- "AI SaaS and fintech" is three different ICPs with different procurement cycles, compliance requirements, and willingness to pay. No segment validated.
- The MIT license removes upgrade pressure for the exact companies capable of self-hosting and seriously evaluating the product.

**What actually happened:** Lotus ran out of runway without converting open-source enthusiasm into enterprise contracts. Post-mortem confirms ICP clarity and monetization model as primary causes. The system derived both from founding inputs.

---

### Piano -- Digital Experience Platform

**Input:** Four customer quotes and three metrics. No behavioral segmentation data. No hint about enterprise.

**What the system caught (and what required architectural iteration to surface):**

First two runs without the fixability check: the system generated SMB optimization options. Correctly diagnosed that the metrics were downstream of a segment problem but never surfaced "stop serving this segment" as a recommendation. Enterprise repositioning kept appearing as a buried Steel Man condition.

After adding the fixability check and condition reversal architecture:

- Fixability check correctly identified a structural divide: SMB publishers structurally lack the org capacity to activate the platform. Personalization requires continuous experimentation. These customers don't have a dedicated person whose job it is to run it.
- "CONSIDER ABANDONMENT: SMB publishers can't generate the audience scale or operational capacity for personalization to produce measurable ROI. No onboarding improvement changes this math."
- Option A elevated to primary recommendation: Move upmarket to mid-size and enterprise publishers. Rebuild GTM around removal cost, not feature adoption.
- Behavioral mechanic: Conforming Software. After 12 months of personalization campaigns, the platform knows the publisher's audience better than any alternative. Switching cost becomes a knowledge cost.

**What actually happened:** Piano repositioned fully to enterprise. D90 retention jumped from 8% to 67%. CAC payback dropped from 22 months to 8 months.

**The architectural story:** Piano is the clearest example of why the fixability check mattered. Without it, the system kept trying to fix a situation that needed to be abandoned. The question it had never been forced to ask: is this a fixable distance or a structural divide? Once forced to answer that, the correct recommendation surfaced.

---

### Duolingo -- 2018 Growth Crisis

**Input:** Pre-intervention signals. Two failed experiments documented. Clean user quotes. No mention of what actually worked.

**What the system caught:**
- Signal 3: "The moves counter failed because it manufactured artificial loss, not earned loss. Loss aversion requires prior investment to work. You have to lose something you earned." The system derived the exact insight Jorge Mazal documents as his key learning, from one user quote about a streak and one failed experiment.
- Signal 4: "The referral program tried to use friendship to grow acquisition. The actual signal is that friendship creates removal cost. Stopping means becoming invisible to someone you started something with. That's a retention mechanic, not an acquisition mechanic."
- Option A: Visible streak counter. Loss aversion applied to earned progress, not manufactured scarcity.
- Option B: Friend accountability loop. Social removal cost rather than competitive pressure. "The friend isn't a reward. The friend is infrastructure."
- Correct sequencing: validate streak first, layer social on top, reframe around entertainment only if both fail.

**What actually happened:** Duolingo built leaderboards, streaks, and notification optimization in roughly that order. DAU grew 4.5x over four years.

**Honest note:** The system recommended streak counter and friend accountability loop. Duolingo built leaderboards as the first social mechanic, which is more competitive than what the system suggested. The sequencing and core mechanisms were correct. The specific implementation differed.

---

### Keyhole -- Social Analytics Platform

**Input:** Funnel data, four user quotes, and one buried behavioral observation: Saturday signups convert at roughly half the rate of weekday signups.

**The buried signal:** The Saturday drop was listed as one of six behavioral observations with no label on its significance. The system identified it as the most important data point in the entire input.

**What the system caught:**
- Signal 4: "The Saturday signal is a direct window into what your product does without a human present. Your team doesn't work weekends. The product does. And the product, alone, converts at half the rate. That's your baseline self-serve number made visible."
- `WRONG_METRIC` -- Trial-to-paid conversion (8%) measures a buying decision. Activation rate measures whether users have actually experienced the product. You can't convert someone who hasn't activated. Optimizing the sales motion while 60% of users never connect an account is optimizing the wrong stage.
- Recommendation: Identify exactly what the walkthrough does in 15 minutes that self-serve doesn't, then build that mechanism into the product. Not "improve onboarding." The right framing: what does the walkthrough person show or say that moves a user from uncertainty to conviction?
- Option A implementation: brand name input at signup generates a sample dashboard before any account connection. Show users what the product looks like with their data before asking them to set anything up.

**What actually happened:** Keyhole refined onboarding, added PLG mechanics, reduced signup friction. ARR up 25%. Net revenue retention 65-70%.

**Honest gap:** Keyhole's first proof point was a single "Sign Up with Google" button -- reducing friction at the very top of funnel before users even reached the product. The system recommended fixing activation inside the product. Right direction, missed the most upstream intervention.

---

## The Two Architectural Additions That Changed Everything

Two late additions produced the biggest quality jumps in the whole build. Both came from finding systematic gaps in real validation runs, not from theory.

### The Fixability Check

The system kept generating optimization options when the correct answer was abandonment. Piano ran three times. Without the fixability check, every single run produced SMB optimization options. The enterprise repositioning signal kept showing up as a buried Steel Man condition, present but never actionable.

The fixability check forces one question before any recommendation gets generated:

**Is this a fixable distance or a structural divide?**

Fixable distance means the product direction is right but delivery, activation, or positioning needs work. Optimization closes the gap.

Structural divide means the current segment structurally lacks what the product needs to deliver value. Not because of bad onboarding. Because of capabilities, behaviors, resources, or scale they can't provide no matter what you build. No optimization closes that.

When the check finds a structural divide with strong converging evidence, it flags CONSIDER ABANDONMENT before generating any options. That's the question the system had never been forced to ask. Once forced to ask it, Piano surfaced enterprise repositioning as a primary recommendation instead of a footnote.

It also fired correctly on Duolingo: casual browsers structurally lack external language stakes. No notification improvement creates a job that doesn't exist. The system stopped recommending notification tweaks and started asking what would make return feel necessary rather than optional.

### The Condition Reversal Check

Here's the thing about Steel Man conditions: the system kept generating the correct answers in the wrong place.

Piano's Steel Man contained: "If the structural divide is a small/mid-market problem rather than a product problem, the right answer is not to compress the product but to move upmarket." That's the correct recommendation sitting inside a failure condition. A PM reading it would note it as a risk. They wouldn't act on it.

After every Steel Man is generated, the system now asks: if any of these conditions turned out to be true, would it point toward a better recommendation than the one already made? If yes, elevate it as a named option with full reasoning and implementation detail.

A stronger answer buried as a footnote is still a buried answer. Both additions came from running the system on real companies and finding the same gap repeatedly, not from prompt engineering intuition.

---

## How It Works

```
Raw signals (interviews, reviews, usage logs, support tickets)
      |
      v
Silent bias detection [Haiku -- fast, cheap]
      |
      PROXY_PAIN / WORKAROUND / WRONG_METRIC / RESEARCH_DECISION_GAP
      |
      v
Fixability check [before any recommendation]
      |
      FIXABLE DISTANCE: proceed to options
      STRUCTURAL DIVIDE + STRONG evidence: flag CONSIDER ABANDONMENT
      |
      v
Full analysis with frameworks [Sonnet -- quality]
JTBD · Growth Loops · 7 Powers · Behavioral Mechanics Library
      |
      v
Two-tier recommendation
      |
      TIER 1: executable within active constraints
      TIER 2: strategically important but constraint-blocked
              with explicit trigger conditions for when to revisit
      |
      v
Steel Man (required, not optional)
      |
      Condition Reversal Check: elevate stronger answers from
      failure conditions to named options
      |
      v
Hypotheses with Leverage x Risk matrix
RUN FIRST / RUN SECOND / RUN THIRD / DEPRIORITIZE
      |
      v
Experiment designs with alternatives and switching conditions
      |
      v
Interpret results -- confirmed / invalidated / inconclusive
      |
      v
Context updates automatically
Research memory compounds across sessions
```

Model routing: Haiku for bias detection and constraint parsing. Sonnet for output generation. Cost and latency logged on every run.

---

## Hypotheses and Experiment Design

Surfacing signals is useful. Knowing what to test next is what actually changes product decisions.

### What a hypothesis is in this system

Four required parts, all of them:

```
We believe:        [specific claim about user behavior or need]
Because:           [direct quote or signal from Stage 1, not inference]
This addresses:    [which bias flag fired: PROXY_PAIN / WORKAROUND /
                   WRONG_METRIC / RESEARCH_DECISION_GAP]
We'd be wrong if:  [the Steel Man condition that would kill this]
```

If you can't state what would make it wrong, it's not a hypothesis. It's an opinion. The system won't generate it.

Risk levels mean specific things and aren't arbitrary:

```
HIGH:   If wrong, we build entirely the wrong thing
MEDIUM: If wrong, the product needs to be meaningfully
        better than the existing workaround
LOW:    If wrong, this is a positioning or communication
        problem, not a product problem
```

### Two types of hypotheses, not one flat list

**Recommendation hypotheses** are tied directly to Stage 1 options. One per recommendation. If Stage 1 produced Option A, B, and an elevated Option C, you get three hypotheses. Each one asks: what single thing needs to be true for this option to be the right call? Risk and leverage scores are meaningful because HIGH leverage means "if this is wrong, Option A is off the table entirely" not just "this seems important."

**Frame-breakers** are 1-2 hypotheses that challenge the entire diagnostic frame. Not variations on the options. The ones that would make all three recommendations irrelevant if true. They should feel slightly uncomfortable to include. If they don't, they're not frame-breaking enough.

Maximum five hypotheses per run. The discipline is the point.

### What makes a good experiment

Three criteria in order of importance:

**Speed** -- how fast does this tell us if we're right or wrong? A 2-day test beats a 2-month test even if the 2-month test is more rigorous.

**Cost of being wrong** -- if the hypothesis is false, what did we waste? Code is expensive. A landing page is cheap. A conversation is free.

**Signal clarity** -- does the experiment produce a clear yes or no, or just more ambiguity?

The system always recommends the cheapest experiment that can still answer the question. That's the discipline most PMs skip because the more interesting experiments feel more rigorous.

### The experiment hierarchy

```
Conversation     fastest, free, lowest signal clarity
Fake door        fast, needs traffic, medium clarity
Prototype        medium speed, some build cost, high clarity
Wizard of Oz     slower, manual ops cost, high clarity
Concierge        slowest, high ops cost, highest clarity
```

For each hypothesis the system outputs:

- Primary experiment recommendation with a "why this type" explanation
- Specifically what to build or do
- Who to test with
- Success looks like: a measurable behavior, not an opinion
- Failure looks like: exactly what kills the hypothesis
- Time to run and cost if wrong
- Two alternatives with specific switching conditions ("better if you don't have web traffic yet")
- ONLY BUILD IF: one sentence naming the confirmed condition before committing to a build

The alternatives aren't a menu. Each one has a switching condition -- a specific situation where you'd use it instead of the primary. That's what lets a PM self-select correctly without needing to understand experiment design theory.

### Interpret results

After running an experiment in the real world, paste the results back in. The system evaluates against the original hypothesis and the Steel Man condition that generated it, not just a generic confirmed/invalidated verdict.

Output structure:

```
BIAS PATTERN REVISITED:
Which bias flag generated this hypothesis?
Was the flag correct?

STEEL MAN RESOLUTION:
Did the experiment trigger the failure condition?
YES: recommendation must change
NO: original recommendation holds

VERDICT: CONFIRMED / INVALIDATED / INCONCLUSIVE

IF CONFIRMED: minimum viable thing to build now
IF INVALIDATED: revised hypothesis to test instead
IF INCONCLUSIVE: specific data point that would resolve it
```

The loop closes. Signal to bias to hypothesis to experiment to interpretation to context update. The next run knows what you already learned.

---

## Tradeoffs


| Decision | What I chose | What I gave up | Why |
|---|---|---|---|
| 4 workflows to 2 | Process signals and interpret | Feature prioritization workflow | Features are downstream of validated hypotheses. Scoring features before hypotheses are validated is scoring the wrong things with false precision. |
| Hard constraint filtering to two-tier | Tier 1 now, Tier 2 with triggers | Clean simple output | Hard filtering kills useful insights. A constraint shouldn't hide a strategically important recommendation just because it's not immediately executable. |
| Menu-based constraints to natural language | Plain language parsed by Haiku | Structured 13-option menu | The menu was too specific to the first companies tested. Natural language parsed into structured categories works for any company in any context. |
| Self-populating context to progressive | Context builds from real runs | Rich upfront setup | A PM who fills out six files on day one rarely does. A system that learns from actual runs compounds without friction. |
| Specific implementations to mechanism plus library | "Loss aversion via streak counter" | "Build streaks" | The system should reason to mechanisms first. Streaks drive retention for language learning. They destroy it for meditation apps. Same mechanism, opposite outcomes. |
| Optimization-first to fixability check | Ask whether to optimize or abandon | Always generating options | The system kept recommending ways to fix situations that needed to be walked away from entirely. |
| Buried Steel Man insights to condition reversal | Elevate stronger answers to recommendations | Cleaner Steel Man section | The system was generating correct answers in the wrong section. A failure condition that implies a better recommendation than the primary one shouldn't stay buried. |

**The honest limitation:** The system consistently surfaces root causes over downstream optimizations. It's built to catch what PMs miss, not to generate sprint backlogs. A PM who wants to know what to ship this week needs to combine system output with their own judgment about what's actually executable. The system tells you what's wrong. It doesn't always name the fastest path to fixing it. That's a deliberate design choice.

---

## Behavioral Mechanics Library

The system doesn't recommend "build streaks." It reasons to mechanisms and cross-references a library that maps those mechanisms to proven implementations and, critically, to when each one backfires.

Seven mechanisms currently documented:

**Conforming Software** -- the product morphs to the user with every interaction. Switching cost becomes emotional. Right for AI-native tools with rich usage data. Fails when personalization is superficial or invisible.

**Workflow Dependency / Removal Cost** -- users return because turning the product off would break their actual work. Right for tools that touch recurring unavoidable tasks. Fails when the product is still discretionary.

**Loss Aversion** -- people are more motivated by avoiding loss than achieving gain. Right for daily habit products with earned progress. Fails critically for meditation and wellness apps where loss aversion creates guilt and destroys the core value proposition.

**Flow State / Difficulty Adjustment** -- real-time adaptation keeps users in the productive zone. Right for learning products with skill curves. Fails when adaptation is visible and feels manipulative.

**Social Investment Loop** -- using the product naturally invites or benefits others. Right for products with natural sharing moments. Fails when inviting others feels like burdening them.

**Variable Reward** -- unpredictable positive outcomes create return behavior. Right for entertainment and discovery products. Fails critically for productivity tools where unpredictability feels like inefficiency.

**Cognitive Offloading with Guardrails** -- AI does the thinking, user makes the call. Right for AI-native tools where users want to feel smarter, not replaced. Fails when offloading is complete and users feel the product is a crutch.

---

## File Structure

```
pm-discovery-os/
├── workflows/
│   ├── process_signals.py          CLI: Stage 1 + Stage 2 + Interpret
│   └── process_signals_api.py      Web: non-interactive API wrapper
├── knowledge/
│   ├── frameworks.md               JTBD, Growth Loops, 7 Powers
│   ├── behavioral-mechanics.md     Mechanisms + when they backfire
│   ├── prioritization-frameworks.md  DHM, Leverage x Risk, Speed to Signal
│   └── company-context.md          Auto-populated research memory
├── evals/
│   └── process-signals-rubric.md   Scoring criteria written before any workflow code
├── runs/
│   └── log.json                    Every run: tokens, latency, score
├── app.py                          Flask web server on port 5000
├── index.html                      Web interface
└── CLAUDE.md                       System instructions + compounding corrections
```

The evaluation rubric was written before any workflow code. Every run is scored automatically. When output is wrong, the fix goes into CLAUDE.md permanently and never repeats.

---

## Web Interface

```bash
git clone https://github.com/shreyasjena123/discovery-os
cd discovery-os
pip3 install flask flask-cors anthropic
python3 app.py
```

Open `http://localhost:5000` and enter your Anthropic API key. Stored locally in your browser, never sent anywhere.

---

## CLI Setup

```bash
git clone https://github.com/shreyasjena123/discovery-os
cd discovery-os
pip3 install anthropic
export ANTHROPIC_API_KEY="your-key-here"
python3 workflows/process_signals.py
```

Add to `~/.zshrc` to make permanent:

```bash
echo 'export ANTHROPIC_API_KEY="your-key-here"' >> ~/.zshrc
echo 'alias pmos="cd /path/to/discovery-os && python3 workflows/process_signals.py"' >> ~/.zshrc
source ~/.zshrc
```

---

## What's Next

**Interpret-then-evaluate:** A workflow that takes a proposed solution and checks whether it addresses the confirmed hypothesis or solves the wrong layer. Would have caught Nabla's original broad platform approach before the rebuild.

**Automated eval runner:** Batch test cases against known post-mortem outcomes. The six case studies with confirmed outcomes become regression tests that catch prompt regressions when knowledge files change.

**Abandonment reasoning depth:** The fixability check correctly identifies structural divides. The next step is generating the alternative path with the same rigor as a primary recommendation, not just flagging that abandonment is right.

---

## About

Built by Shreyas Jena, graduating June 2026.

Built entirely in Claude Code. Four days. Six real validation runs.
