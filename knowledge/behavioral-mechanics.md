# Behavioral Mechanics Library

## How to use this library
When a recommendation identifies a retention 
or engagement problem, use this library to:
1. Identify which mechanism fits the product 
   context
2. Select the right implementation for that 
   mechanism
3. Flag when a mechanism would backfire

Always match mechanism to product type before 
selecting implementation. The same mechanic 
that works in one context destroys retention 
in another.

---

## MECHANISM SELECTION FRAMEWORK

Before selecting any mechanism run this audit:

INTERNAL TRIGGER CHECK:
What emotion or context makes users open 
the product without a notification?
- If none exists: you are relying on external 
  triggers and will lose long term
- If exists: build around it, not against it

INVESTMENT / STORE OF VALUE TEST:
Does the product get meaningfully better 
or more personal with use?
- Yes: focus on switching cost and investment
- No: you have low retention ceiling regardless 
  of mechanics added

REMOVAL COST TEST (AI-native filter):
What literally breaks for the user if they 
delete the app?
- High removal cost: workflow dependency exists
- Low removal cost: product is still optional

CONTEXT FIT:
Match mechanism to product category:
- Learning / habit apps → flow-state difficulty 
  adjustment + loss aversion
- Social / entertainment → conforming software 
  + parasocial relationships
- Tools / productivity → workflow embedding 
  + removal cost
- AI-native products → conforming + cognitive 
  offloading with guardrails

---

## MECHANISM 1: Conforming Software

Core principle: The product literally morphs 
to the user with every interaction — UI, 
defaults, suggestions, and functionality 
become more personalized over time. 
Switching cost becomes emotional not just 
functional.

When it works:
- Product has enough surface area to personalize
- Users interact frequently enough to generate 
  meaningful behavioral signal
- Personalization is visible and felt by user
- Product category values individual preference

When it backfires:
- Personalization is superficial or invisible
- Users interact too infrequently to generate 
  signal
- Product category is standardized and users 
  want consistency not personalization

AI-native implementation:
Every interaction should make the next 
interaction feel more tailored. Store user 
decisions, corrections, preferences, and 
past outputs. Reference them in future runs.
Example: PM Discovery OS research history 
that compounds across sessions — each run 
makes the next analysis more specific to 
your company context.

Traditional implementation:
UI defaults that adjust to usage patterns,
recommendation algorithms that improve with 
history, content feeds that reflect past behavior.
Example: Snapchat memories making older 
cohorts more retained than newer ones.

---

## MECHANISM 2: Workflow Dependency / Removal Cost

Core principle: Users return because turning 
the product off would break their actual 
work or life flow. The product becomes 
infrastructure not entertainment.

When it works:
- Product solves a recurring unavoidable task
- No adequate substitute exists once embedded
- Switching requires rebuilding accumulated 
  context or workflow
- Product touches something that happens 
  regardless of motivation

When it backfires:
- Product is discretionary not necessary
- Substitutes exist that are easier to adopt
- Workflow embedding requires too much 
  upfront setup cost
- Users perceive dependency as a trap 
  not a benefit

AI-native implementation:
Optimize for removal cost not DAU.
Ask: what breaks if we turn this off?
Build features that make the answer 
increasingly painful.
Example: A PM who has run 20 discovery 
sessions in your system has research history,
confirmed hypotheses, and context that 
exists nowhere else. Removal cost is high.

Traditional implementation:
API integrations that make the product 
part of existing workflows, data that 
lives only in the product, team features 
that create social switching costs.

---

## MECHANISM 3: Loss Aversion

Core principle: People are more motivated 
by avoiding loss than achieving equivalent 
gain. Works when there is something of 
perceived value at risk.

When it works:
- User has already invested time or progress
- The thing at risk is visible and personal
- Daily use case exists naturally
- Reset or loss feels meaningful not arbitrary

When it backfires:
- Product is anxiety-sensitive: meditation, 
  therapy, mental health, wellness
  Reason: loss aversion creates guilt and 
  shame which destroys the core value prop
- User base is professional and senior
  Reason: feels gamified and juvenile
- Use case is weekly or irregular not daily
  Reason: streak mechanics require daily cadence
- Stakes feel trivial relative to effort required

Proven implementations:
Streak counter: consecutive day count that 
resets on missed day
Works for: language learning, fitness, 
daily productivity
Fails for: wellness, meditation, B2B tools

League and leaderboard: weekly competition 
with promotion and demotion
Works for: large consumer bases, products 
with natural competitiveness
Fails for: small user bases, sensitive categories

Financial commitment: real money at stake
Works for: high motivation volatility, 
behaviors with objective verification
Fails for: low-stakes habits, income-sensitive users

Selection rule: Match implementation intensity 
to emotional weight of the habit.
Gym attendance → financial commitment
Language learning → streak counter
Meditation → never loss aversion

---

## MECHANISM 4: Flow State / Difficulty Adjustment

Core principle: Users stay engaged when 
challenge level matches their current 
ability — not too hard, not too easy. 
Real-time adaptation keeps users in 
the productive zone.

When it works:
- Product has a skill progression curve
- Performance can be measured objectively
- Adaptation can happen in real time
- Users feel the adjustment without 
  being aware of the algorithm

When it backfires:
- Skill level is not meaningfully measurable
- Users want consistent experience not 
  adaptive one
- Adaptation is visible and feels manipulative
- Product category does not have natural 
  difficulty curve

AI-native implementation:
Adjust output complexity, depth, and framing 
based on user expertise signals. A PM who 
consistently edits outputs toward more 
strategic framing gets more strategic output.
A PM who asks follow-up questions gets 
more granular output by default.

Traditional implementation:
Duolingo Birdbrain algorithm adjusting 
lesson difficulty based on error patterns.
Gaming difficulty curves that respond 
to win/loss ratios.

---

## MECHANISM 5: Social Investment Loop

Core principle: Using the product naturally 
invites or benefits others, bringing the 
user's network in and creating social 
switching costs.

When it works:
- Product has natural sharing or collaboration 
  moments
- Network effect makes product more valuable 
  with more users
- Inviting others feels generous not spammy
- Social graph already exists or is easily formed

When it backfires:
- Product is individual and private by nature
- Inviting others feels like burdening them
- No natural collaboration moment exists
- User base is too small for network effects

Implementations:
Collaborative features that require others,
shareable outputs that market the product,
referral programs tied to real product value 
not just discounts,
team features that create group switching cost.

Selection rule: Social loops require a 
natural moment where sharing feels like 
giving value not asking for a favor.

---

## MECHANISM 6: Variable Reward

Core principle: Unpredictable positive 
outcomes create compulsive return behavior. 
The anticipation of reward is often more 
motivating than the reward itself.

When it works:
- Product category is entertainment or discovery
- Reward is genuinely variable not fake random
- Users have time and attention to burn
- Dopamine hit is the core value prop

When it backfires:
- Product category is productivity or tools
  Reason: productivity users need clarity 
  and control not unpredictability. 
  Binge once then feel drained and churn.
- Users have limited time and high intentionality
  Reason: unpredictability feels like 
  inefficiency not delight
- Variable reward is the only mechanism
  Reason: fatigues fast without investment 
  or conforming to sustain it

Implementations:
Infinite scroll for entertainment products,
discovery feeds for social and content,
randomized rewards for gaming.

Selection rule: Variable reward works for 
entertainment. Productivity needs certainty 
and control reward instead.

---

## MECHANISM 7: Cognitive Offloading with Guardrails

Core principle: AI does the thinking but 
the best products force light investment 
from the user — editing output, making 
decisions, confirming recommendations — 
so users feel agency not dependency.

When it works:
- AI capability is high enough to produce 
  genuinely useful output
- User investment step is lightweight not burdensome
- Users feel smarter and more capable not replaced
- Output is something user can own and act on

When it backfires:
- Pure offloading with no user investment
  Reason: studies show complete cognitive 
  offloading hurts long-term retention 
  because users feel the product is a crutch
- Investment step is too heavy
  Reason: defeats the purpose of AI assistance
- Output quality is low enough that editing 
  feels like doing it yourself

AI-native implementation:
Every workflow should have a moment where 
the user makes a decision — selecting 
hypotheses, choosing between options, 
confirming a recommendation. This creates 
ownership and investment.
Example: PM Discovery OS hypothesis selection 
gate — user selects which hypotheses to 
experiment on. The system did the hard work. 
The user made the call.

---

## FAILURE PATTERN LIBRARY

Common mistakes when applying behavioral mechanics:

COPYING WITHOUT CONTEXT:
Streaks work for Duolingo, backfire for 
meditation apps. Same mechanism, opposite 
emotional outcome. Always ask: what emotion 
does this mechanic create in this context?

EXTERNAL TRIGGERS WITHOUT INTERNAL ITCH:
Push notifications only work when they 
scratch an emotion the user already feels. 
Without internal trigger, notifications 
become spam regardless of timing optimization.

VARIABLE REWARD IN PRODUCTIVITY TOOLS:
TikTok-style infinite scroll copied into 
productivity tools causes binge then burnout. 
Productivity users need control not 
unpredictability.

LOSS AVERSION IN ANXIETY-SENSITIVE CATEGORIES:
Streak mechanics in wellness apps create 
guilt and shame which directly undermines 
the core value proposition. The mechanic 
that drives Duolingo retention destroys 
meditation app retention.

GAMIFICATION FOR PROFESSIONAL AUDIENCES:
Leaderboards and badges feel juvenile in 
B2B and enterprise contexts. Professional 
users want to feel competent not competitive.
