import anthropic
import json
import re
from typing import Optional
import time
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

WORKFLOW_FILE = SCRIPT_DIR / "process-signals.md"
FRAMEWORKS_FILE = PROJECT_ROOT / "knowledge" / "frameworks.md"
RUNS_DIR = PROJECT_ROOT / "runs"
LOG_FILE = RUNS_DIR / "log.json"

MODEL_BIAS = "claude-haiku-4-5-20251001"
MODEL_OUTPUT = "claude-sonnet-4-6"


def load_file(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()


def get_multiline_input() -> str:
    print("Paste your signals below (press Enter twice when done):")
    return get_multiline_input_raw()


def extract_rubric_score(output: str) -> Optional[int]:
    match = re.search(r"RUBRIC SCORE.*?(\d+)\s*/\s*8", output, re.IGNORECASE)
    if match:
        return int(match.group(1))
    scores = re.findall(r"\b([0-2])\b", output)
    if len(scores) >= 4:
        total = sum(int(s) for s in scores[:4])
        if 0 <= total <= 8:
            return total
    return None


def flag_correction(stage1_output: str) -> None:
    """Ask user what went wrong, derive a rule via API, and append to CLAUDE.md."""
    issue = input("What went wrong? Describe the issue in one sentence: ").strip()
    if not issue:
        print("No issue provided. Skipping.")
        return

    # Derive a concrete rule via haiku
    client = anthropic.Anthropic()
    try:
        response = client.messages.create(
            model=MODEL_BIAS,
            max_tokens=100,
            messages=[
                {
                    "role": "user",
                    "content": (
                        "Convert this issue description into a one-line rule "
                        "for an AI system. Start with a verb. Be specific not general.\n\n"
                        f"Issue: {issue}\n\n"
                        "Return only the rule, nothing else."
                    ),
                }
            ],
        )
        rule = response.content[0].text.strip()
    except Exception as e:
        rule = f"(Rule derivation failed: {e})"

    # Build the input summary from the first ~80 chars of stage1_output
    run_summary = stage1_output[:80].replace("\n", " ").strip()
    if len(stage1_output) > 80:
        run_summary += "..."

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    entry = (
        f"\n---\n"
        f"Date: {timestamp}\n"
        f"Run: {run_summary}\n"
        f"Issue: {issue}\n"
        f"Fix: {rule}\n"
        f"---"
    )

    claude_md = PROJECT_ROOT / "CLAUDE.md"
    if claude_md.exists():
        content = claude_md.read_text()
        if "## Learned Corrections" in content:
            # Append after the section header line
            content = content.replace(
                "## Learned Corrections\n[This section auto-populates when the user \nflags an output as wrong. Do not edit manually.]",
                "## Learned Corrections\n[This section auto-populates when the user \nflags an output as wrong. Do not edit manually.]" + entry,
            )
            claude_md.write_text(content)
            print(f"\nLogged to CLAUDE.md:\nFix: {rule}")
        else:
            print("Warning: ## Learned Corrections section not found in CLAUDE.md.")
    else:
        print("Warning: CLAUDE.md not found.")


def gate_prompt(stage1_output: str) -> tuple[Optional[str], str]:
    """Display the gate menu and return (selection, final_stage1_output)."""
    while True:
        print("\n" + "-" * 40)
        print("[Y] Proceed to Stage 2")
        print("[R] Re-run Stage 1 with new input")
        print("[E] Edit Stage 1 output before Stage 2")
        print("[I] Interpret experiment results")
        print("[F] Flag something as wrong to fix permanently")
        print("[Q] Save and quit")
        print("-" * 40)
        choice = input("Select: ").strip().upper()

        if choice == "Y":
            return "Y", stage1_output

        elif choice == "R":
            return "R", stage1_output

        elif choice == "E":
            print("\nCurrent Stage 1 output (edit below, press Enter twice when done):")
            print(stage1_output)
            print("\n--- Enter edited output below ---")
            edited = get_multiline_input_raw()
            if edited.strip():
                stage1_output = edited
            print("\n--- Updated output ---")
            print(stage1_output)

        elif choice == "I":
            return "I", stage1_output

        elif choice == "F":
            flag_correction(stage1_output)

        elif choice == "Q":
            return "Q", stage1_output

        else:
            print("Invalid selection. Enter Y, R, E, I, F, or Q.")


def get_multiline_input_raw() -> str:
    """Collect multiline input without the prompt header."""
    lines = []
    blank_count = 0
    while True:
        line = input()
        if line == "":
            blank_count += 1
            if blank_count >= 2:
                break
            lines.append(line)
        else:
            blank_count = 0
            lines.append(line)
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def update_context(raw_input: str, stage1_output: str) -> bool:
    """Append a run summary to Research History in company-context.md. Returns True if updated."""
    context_file = PROJECT_ROOT / "knowledge" / "company-context.md"
    if not context_file.exists():
        return False

    # Extract bias flags that fired (non-empty values in BIAS FLAGS section)
    bias_flags_match = re.search(r"BIAS FLAGS:(.*?)(?:RECOMMENDATION:|STEEL MAN:|RUBRIC|$)", stage1_output, re.IGNORECASE | re.DOTALL)
    fired = []
    if bias_flags_match:
        for flag in ("PROXY PAIN", "WORKAROUND", "WRONG METRIC", "RESEARCH-DECISION GAP"):
            if re.search(re.escape(flag), bias_flags_match.group(1), re.IGNORECASE):
                fired.append(flag)

    # Extract first sentence of recommendation
    rec_match = re.search(r"RECOMMENDATION:\s*\n?(.*?)(?:\n|\.)", stage1_output, re.IGNORECASE | re.DOTALL)
    rec_direction = rec_match.group(1).strip() if rec_match else "—"

    timestamp = datetime.now(timezone.utc).isoformat()
    product_snippet = raw_input.strip().replace("\n", " ")[:100]
    flags_str = ", ".join(fired) if fired else "none"

    entry = (
        f"\n---\n"
        f"Run: {timestamp}\n"
        f"Product analyzed: {product_snippet}\n"
        f"Key bias flags fired: {flags_str}\n"
        f"Recommendation direction: {rec_direction}\n"
        f"---"
    )

    content = context_file.read_text()
    if "## Research History" in content:
        content = content.replace("## Research History", f"## Research History{entry}", 1)
    else:
        content += f"\n## Research History{entry}\n"

    context_file.write_text(content)
    return True


def run_interpret() -> None:
    """Interpret experiment results against a prior hypothesis."""
    client = anthropic.Anthropic()
    context_file = PROJECT_ROOT / "knowledge" / "company-context.md"
    timestamp = datetime.now(timezone.utc).isoformat()

    # Step 1: Collect hypothesis in plain language
    print(
        "Describe the hypothesis you tested in plain language. Include:\n"
        "- What you believed was true\n"
        "- Why you believed it\n"
        "- What would have proven you wrong\n\n"
        "(You can paste a hypothesis from a previous run or write it fresh)"
    )
    hypothesis_text = input("Hypothesis: ").strip()
    if not hypothesis_text:
        print("No hypothesis provided. Exiting interpretation.")
        return

    # Step 2: Load framework files and active constraints
    frameworks_text = ""
    frameworks_file = PROJECT_ROOT / "knowledge" / "frameworks.md"
    if frameworks_file.exists():
        frameworks_text += load_file(frameworks_file)

    prioritization_file = PROJECT_ROOT / "knowledge" / "prioritization-frameworks.md"
    if prioritization_file.exists():
        frameworks_text += "\n\n" + load_file(prioritization_file)

    interpret_constraints = ""
    if context_file.exists():
        context_content = context_file.read_text()
        constraints_match = re.search(
            r"## Active Constraints\s*\n(.*?)(?=\n##|\Z)",
            context_content,
            re.DOTALL,
        )
        if constraints_match:
            extracted = constraints_match.group(1).strip()
            if extracted and extracted != "None specified":
                interpret_constraints = extracted

    # Step 3: Collect results
    print("\nPaste your experiment results, transcript, or notes below (press Enter twice when done):")
    results_input = get_multiline_input_raw()
    if not results_input.strip():
        print("No results provided. Exiting interpretation.")
        return

    # Step 4: Single API call
    frameworks_section = (
        f"Load and reference these frameworks before interpreting:\n{frameworks_text}\n\n"
        if frameworks_text else ""
    )

    constraints_section = ""
    if interpret_constraints:
        constraints_section = (
            f"ACTIVE CONSTRAINTS:\n{interpret_constraints}\n\n"
            "Apply two-tier structure throughout:\n\n"
            "IF CONFIRMED — WHAT TO BUILD NOW:\n\n"
            "TIER 1 — WITHIN CONSTRAINTS:\n"
            "Minimum viable solution executable now.\n"
            "Never recommend something that violates an active constraint in Tier 1.\n\n"
            "TIER 2 — BEYOND CONSTRAINTS:\n"
            "What you would build if constraints lifted.\n"
            "Label with which constraint conflicts.\n"
            "Include what this unlocks.\n"
            "Include specific trigger for when to revisit.\n\n"
            "IF INVALIDATED — REVISED HYPOTHESIS:\n"
            "Revised hypothesis must be testable within Tier 1 constraints.\n"
            "If no Tier 1 revision exists generate a Tier 2 revision and flag "
            "what needs to change to test it.\n\n"
            "IF INCONCLUSIVE — WHAT IS MISSING:\n"
            "Identify whether the missing data point is collectible within Tier 1 constraints.\n"
            "If not, flag as Tier 2 and specify what constraint needs to lift.\n\n"
            "When scoring DHM:\n"
            "Factor constraint feasibility into Hard to Copy score.\n"
            "Note explicitly if a solution requires capabilities outside constraints.\n\n"
            "Never suppress a strategically important insight because of a constraint.\n"
            "Always surface it in Tier 2.\n\n"
        )

    interpret_system = (
        "You are a product discovery analyst interpreting "
        "experiment results against the original hypothesis "
        "and reasoning chain that generated it.\n\n"
        f"{frameworks_section}"
        f"{constraints_section}"
        f"Original hypothesis being tested:\n{hypothesis_text}\n\n"
        "Your output must follow exactly this structure:\n\n"
        "HYPOTHESIS TESTED:\n"
        "[restate the full hypothesis including "
        "We believe / Because / We'd be wrong if]\n\n"
        "BIAS PATTERN REVISITED:\n"
        "Which bias flag generated this hypothesis:\n"
        "[PROXY_PAIN / WORKAROUND / WRONG_METRIC / "
        "RESEARCH_DECISION_GAP]\n\n"
        "Was the bias flag correct?\n"
        "- YES: The bias was real — users were masking "
        "a deeper need than they stated\n"
        "- NO: The stated request was accurate — "
        "the surface ask was the real ask\n"
        "Evidence: [specific quote or data point "
        "from results that resolves this]\n\n"
        "STEEL MAN RESOLUTION:\n"
        "Original condition that would invalidate "
        "this hypothesis:\n"
        "[restate the we'd be wrong if condition]\n\n"
        "Did the experiment trigger this condition?\n"
        "- YES — the Steel Man was true, recommendation "
        "must change\n"
        "- NO — the Steel Man did not fire, original "
        "recommendation holds\n"
        "Evidence: [specific quote or data point]\n\n"
        "VERDICT: [CONFIRMED / INVALIDATED / INCONCLUSIVE]\n\n"
        "EVIDENCE:\n"
        "[3-5 specific quotes or data points from "
        "experiment results that support verdict]\n\n"
        "WHAT THIS MEANS FOR THE PRODUCT:\n"
        "[one paragraph connecting verdict back to "
        "the original recommendation using JTBD or "
        "Growth Loop framework where relevant]\n\n"
        "IF CONFIRMED:\n"
        "What to build now: [minimum viable version]\n"
        "Which growth loop node this strengthens: "
        "[Acquisition/Activation/Retention/Revenue/Referral]\n"
        "DHM quick score: Delight [1-3] / Hard to copy "
        "[1-3] / Margin [1-3]\n\n"
        "IF INVALIDATED:\n"
        "What the data actually shows: [revised belief]\n"
        "Revised hypothesis to test instead: "
        "[new We believe / Because / We'd be wrong if]\n"
        "Which bias pattern was wrong and why:\n"
        "[explain what the bias detector missed]\n\n"
        "IF INCONCLUSIVE:\n"
        "What specific data point is missing:\n"
        "[exactly what would resolve ambiguity]\n"
        "Cheapest way to get that data point:\n"
        "[one experiment, one week max]\n\n"
        "CONTEXT UPDATE:\n"
        "[one sentence for research history log]\n"
        "Bias pattern accuracy: [CORRECT / INCORRECT]\n"
        "Steel Man fired: [YES / NO]"
    )

    print("\n--- Interpreting results ---\n")
    interpret_output = ""
    interpret_tokens: Optional[dict] = None
    interpret_error: Optional[str] = None
    start = time.time()

    try:
        output_parts = []
        with client.messages.stream(
            model=MODEL_OUTPUT,
            max_tokens=4096,
            system=interpret_system,
            messages=[{"role": "user", "content": results_input}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                output_parts.append(text)
            final_message = stream.get_final_message()

        interpret_output = "".join(output_parts)
        interpret_tokens = {
            "input_tokens": final_message.usage.input_tokens,
            "output_tokens": final_message.usage.output_tokens,
        }

        # Step 5: Append to company-context.md
        verdict_match = re.search(r"VERDICT:\s*(CONFIRMED|INVALIDATED|INCONCLUSIVE)", interpret_output, re.IGNORECASE)
        verdict = verdict_match.group(1).upper() if verdict_match else "INCONCLUSIVE"

        context_update_match = re.search(r"CONTEXT UPDATE:\s*\n?(.+)", interpret_output, re.IGNORECASE)
        context_summary = context_update_match.group(1).strip() if context_update_match else "—"

        experiment_entry = (
            f"\n---\n"
            f"Hypothesis: {hypothesis_text[:120].strip()}\n"
            f"Verdict: {verdict}\n"
            f"Date: {timestamp}\n"
            f"Summary: {context_summary}\n"
            f"---"
        )

        if context_file.exists():
            content = context_file.read_text()
            if "## Experiment Results" in content:
                content = content.replace(
                    "## Experiment Results",
                    f"## Experiment Results{experiment_entry}",
                    1,
                )
            else:
                content += f"\n## Experiment Results{experiment_entry}\n"
            context_file.write_text(content)

    except Exception as e:
        interpret_error = str(e)
        print(f"\nInterpretation error: {interpret_error}", flush=True)

    finally:
        latency = round(time.time() - start, 3)
        print("\n")

        # Log to runs/log.json
        RUNS_DIR.mkdir(exist_ok=True)
        existing = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []

        existing.append({
            "timestamp": timestamp,
            "interpret_run": {
                "hypothesis_text": hypothesis_text,
                "results_input_length": len(results_input),
                "output": interpret_output,
                "verdict": re.search(r"VERDICT:\s*(CONFIRMED|INVALIDATED|INCONCLUSIVE)", interpret_output, re.IGNORECASE).group(1).upper() if re.search(r"VERDICT:\s*(CONFIRMED|INVALIDATED|INCONCLUSIVE)", interpret_output, re.IGNORECASE) else None,
                "token_usage": interpret_tokens,
                "latency_seconds": latency,
                "model": MODEL_OUTPUT,
                "error": interpret_error,
            },
        })

        with open(LOG_FILE, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"[Logged to {LOG_FILE}]")


def run_stage2(stage1_output: str) -> None:
    """Run hypothesis generation + experiment design against Stage 1 output."""
    client = anthropic.Anthropic()
    stage2_start = time.time()

    hypothesis_tokens: Optional[dict] = None
    experiment_tokens: Optional[dict] = None
    stage2_output = ""
    stage2_error: Optional[str] = None

    # Load active constraints from company-context.md
    stage2_constraints = ""
    context_file = PROJECT_ROOT / "knowledge" / "company-context.md"
    if context_file.exists():
        context_content = context_file.read_text()
        constraints_match = re.search(
            r"## Active Constraints\s*\n(.*?)(?=\n##|\Z)",
            context_content,
            re.DOTALL,
        )
        if constraints_match:
            extracted = constraints_match.group(1).strip()
            if extracted and extracted != "None specified":
                stage2_constraints = extracted

    try:
        # Call 1: Hypothesis generation (fast/cheap model)
        print("\n--- Stage 2: Generating hypotheses ---\n")

        constraints_block = ""
        if stage2_constraints:
            constraints_block = (
                f"ACTIVE CONSTRAINTS:\n{stage2_constraints}\n\n"
                "Apply two-tier hypothesis structure:\n\n"
                "TIER 1 HYPOTHESIS:\n"
                "Testable within active constraints.\n"
                "Generate minimum 2 Tier 1 hypotheses first.\n"
                "Mark each: [TIER 1 — EXECUTABLE NOW]\n\n"
                "For every Tier 1 hypothesis include:\n"
                "Risk level: [HIGH / MEDIUM / LOW]\n"
                "Leverage level: [HIGH / MEDIUM / LOW]\n"
                "Priority flag: [RUN FIRST / RUN SECOND / RUN THIRD / DEPRIORITIZE]\n"
                "Speed to signal: [HIGH / MEDIUM / LOW]\n\n"
                "Priority rules:\n"
                "HIGH leverage + LOW risk = RUN FIRST regardless of other scores\n"
                "HIGH leverage + HIGH risk = RUN SECOND\n"
                "LOW leverage + LOW risk = RUN THIRD\n"
                "LOW leverage + HIGH risk = DEPRIORITIZE\n\n"
                "Speed to signal rule:\n"
                "If a Tier 1 hypothesis has HIGH speed to signal but lower DHM, flag:\n"
                "FAST VALIDATION FIRST: [one sentence why]\n\n"
                "TIER 2 HYPOTHESIS:\n"
                "High value but requires lifting a constraint.\n"
                "Mark each: [TIER 2 — REQUIRES: constraint name]\n"
                "Include:\n"
                "- What would need to change to test this\n"
                "- What it would unlock if confirmed\n"
                "- Strategic value score [HIGH / MEDIUM / LOW]\n\n"
                "Do not apply risk or leverage scoring to Tier 2 hypotheses "
                "— they are not immediately executable.\n\n"
            )

        hyp_system = (
            "You are a product discovery analyst. Based on the Stage 1 "
            "analysis provided, generate hypotheses in exactly two sections.\n\n"
            + constraints_block
            + "## SECTION 1: RECOMMENDATION HYPOTHESES\n\n"
            "Generate one hypothesis per recommendation option from Stage 1. "
            "If Stage 1 produced Option A, B, and an elevated Option C, generate "
            "three hypotheses. Each one asks: what single thing needs to be true "
            "for this option to be the right call?\n\n"
            "Format each as:\n\n"
            "HYPOTHESIS [A/B/C]: Testing Option [A/B/C]\n\n"
            "Core belief: [one falsifiable sentence]\n\n"
            "If we're wrong: [specific signal that would invalidate this option entirely]\n\n"
            "Leverage: HIGH/MEDIUM/LOW\n"
            "HIGH = being wrong eliminates this option\n"
            "MEDIUM = being wrong requires major rework\n"
            "LOW = being wrong only affects execution\n\n"
            "Risk: HIGH/MEDIUM/LOW\n"
            "HIGH = significant time or build required\n"
            "MEDIUM = some build or user recruitment\n"
            "LOW = data pull or 5 conversations\n\n"
            "Priority: RUN FIRST/SECOND/THIRD based on leverage x risk matrix\n\n"
            "Fastest test: [one specific sentence, cheap enough to actually run]\n\n"
            "## SECTION 2: FRAME-BREAKING HYPOTHESES\n\n"
            "Generate 1-2 hypotheses that challenge the entire diagnostic frame "
            "from Stage 1. These are not variations on the options. They are the "
            "hypotheses that would make all three options irrelevant if true.\n\n"
            "Ask: what is the one thing that, if true, would mean the entire "
            "Stage 1 analysis was looking at the wrong problem?\n\n"
            "These should feel slightly uncomfortable to include. "
            "If they don't, they're not frame-breaking enough.\n\n"
            "Format each as:\n\n"
            "FRAME-BREAKER [1/2]: [short title]\n\n"
            "What if: [the uncomfortable alternative diagnosis in one sentence]\n\n"
            "Why this might be true: [which specific signal from the input could "
            "support this reading if interpreted differently]\n\n"
            "What it would mean: [how this changes the entire recommendation]\n\n"
            "Test: [fastest way to confirm or kill this hypothesis before it wastes time]\n\n"
            "Scoring: Do not apply leverage x risk to frame-breakers. "
            "They are not execution decisions. They are diagnostic challenges. "
            "Label them VALIDATE BEFORE COMMITTING if the evidence supporting them "
            "is stronger than 30% of the signals. "
            "Label them LOW PRIOR if they are speculative with thin evidence.\n\n"
            "TOTAL HYPOTHESES: 3-5 maximum. "
            "Never generate more than 3 recommendation hypotheses "
            "and never more than 2 frame-breakers.\n\n"
            "Return hypotheses only. No preamble."
        )

        hyp_response = client.messages.create(
            model=MODEL_BIAS,
            max_tokens=2048,
            system=hyp_system,
            messages=[{"role": "user", "content": stage1_output}],
        )
        hypotheses = hyp_response.content[0].text
        hypothesis_tokens = {
            "input_tokens": hyp_response.usage.input_tokens,
            "output_tokens": hyp_response.usage.output_tokens,
        }

        print(hypotheses)

        # Hypothesis selection gate
        hyp_numbers = re.findall(r"HYPOTHESIS\s+\[?(\d+)\]?", hypotheses, re.IGNORECASE)
        total_hyps = len(hyp_numbers)

        selected: list[int] = []
        while True:
            print("\n---")
            print("Select hypotheses to design experiments for.")
            print("Enter numbers separated by commas (e.g. 1,3,5)")
            print("Press H to auto-select HIGH risk only")
            print("Press A to select all")
            raw = input("Your selection: ").strip().upper()

            if raw == "A":
                selected = list(range(1, total_hyps + 1))
            elif raw == "H":
                high_blocks = re.findall(
                    r"HYPOTHESIS\s+\[?(\d+)\]?.*?Risk level:\s*HIGH",
                    hypotheses,
                    re.IGNORECASE | re.DOTALL,
                )
                selected = [int(n) for n in high_blocks]
                if not selected:
                    print("No HIGH risk hypotheses found. Please enter numbers manually.")
                    continue
            else:
                try:
                    selected = [int(x.strip()) for x in raw.split(",") if x.strip()]
                    if not selected or any(n < 1 or n > total_hyps for n in selected):
                        print(f"Please enter numbers between 1 and {total_hyps}.")
                        continue
                except ValueError:
                    print("Invalid input. Enter numbers, H, or A.")
                    continue

            # Enforce max 3
            if len(selected) > 3:
                print(
                    f"\nYou selected {len(selected)} hypotheses. For output quality, "
                    "experiment design works best with 3 or fewer.\n"
                    "Which 3 would you like to prioritize?\nRe-enter numbers: ",
                    end="",
                )
                try:
                    raw2 = input().strip()
                    selected = [int(x.strip()) for x in raw2.split(",") if x.strip()]
                    if len(selected) > 3 or any(n < 1 or n > total_hyps for n in selected):
                        print("Still too many or invalid. Please try again.")
                        continue
                except ValueError:
                    print("Invalid input. Please try again.")
                    continue

            break

        # Filter hypothesis text to selected numbers only
        hyp_blocks = re.split(r"(?=HYPOTHESIS\s+\[?\d+\]?)", hypotheses, flags=re.IGNORECASE)
        hyp_blocks = [b for b in hyp_blocks if b.strip()]
        selected_set = set(selected)
        filtered_hypotheses = "\n\n".join(
            block for block in hyp_blocks
            if any(
                re.match(rf"HYPOTHESIS\s+\[?{n}\]?", block.strip(), re.IGNORECASE)
                for n in selected_set
            )
        )

        # Call 2: Experiment design (streaming, higher-quality model)
        print(f"\n--- Stage 2: Designing experiments for hypotheses {selected} ---\n")

        exp_system = (
            "You are a product discovery analyst. For each "
            "hypothesis provided, design the optimal experiment "
            "following these rules:\n\n"
            "EXPERIMENT TYPE SELECTION:\n"
            "Choose based on hypothesis risk level and "
            "available resources:\n\n"
            "Conversation → fastest, free, low signal clarity\n"
            "Fake door → fast, needs traffic, medium clarity\n"
            "Prototype → medium speed, some build cost, high clarity\n"
            "Wizard of Oz → slower, manual ops cost, high clarity\n"
            "Concierge → slowest, high ops cost, highest clarity\n\n"
            "Always recommend cheapest experiment that can "
            "still answer the question clearly.\n\n"
            f"CONSTRAINT CONTEXT: {stage2_constraints if stage2_constraints else 'No specific constraint'}\n"
            "When recommending experiment types, prioritize "
            "experiments that are feasible within this "
            "constraint. A small team cannot run a Wizard "
            "of Oz requiring 40+ hours of manual ops. "
            "A tight budget rules out paid prototype testing. "
            "Adjust recommendations accordingly and "
            "explicitly note if a recommended experiment "
            "requires more resources than the constraint allows.\n\n"
            "For each hypothesis output exactly this structure:\n\n"
            "EXPERIMENT FOR HYPOTHESIS [N]:\n"
            "Recommended type: [experiment type]\n"
            "Why this type: [one sentence reasoning]\n"
            "Specifically: [exactly what you build or do]\n"
            "With: [specific user segment to test with]\n"
            "Success looks like: [measurable behavior, not opinion]\n"
            "Failure looks like: [what kills this hypothesis]\n"
            "Time to run: [X days]\n"
            "Cost if wrong: [what you lose]\n\n"
            "ALTERNATIVES:\n"
            "Option B: [type]\n"
            "Better if: [specific switching condition]\n"
            "Trade-off: [what you gain vs lose]\n\n"
            "Option C: [type]\n"
            "Better if: [specific switching condition]\n"
            "Trade-off: [what you gain vs lose]\n\n"
            "ONLY BUILD IF:\n"
            "[one sentence describing confirmed condition]"
        )

        exp_parts = []
        with client.messages.stream(
            model=MODEL_OUTPUT,
            max_tokens=6000,
            system=exp_system,
            messages=[{"role": "user", "content": filtered_hypotheses}],
        ) as stream:
            for text in stream.text_stream:
                print(text, end="", flush=True)
                exp_parts.append(text)
            exp_final = stream.get_final_message()

        experiments = "".join(exp_parts)
        experiment_tokens = {
            "input_tokens": exp_final.usage.input_tokens,
            "output_tokens": exp_final.usage.output_tokens,
        }

        stage2_output = f"{hypotheses}\n\n{experiments}"

    except Exception as e:
        stage2_error = str(e)
        print(f"\nStage 2 error: {stage2_error}", flush=True)

    finally:
        stage2_latency = round(time.time() - stage2_start, 3)
        print("\n")

        # Append stage2 fields to the most recent log entry
        RUNS_DIR.mkdir(exist_ok=True)
        existing = []
        if LOG_FILE.exists():
            with open(LOG_FILE, "r") as f:
                try:
                    existing = json.load(f)
                except json.JSONDecodeError:
                    existing = []

        if existing:
            existing[-1]["stage2_output"] = stage2_output
            existing[-1]["stage2_hypothesis_tokens"] = hypothesis_tokens
            existing[-1]["stage2_experiment_tokens"] = experiment_tokens
            existing[-1]["stage2_total_latency"] = stage2_latency
            existing[-1]["stage2_error"] = stage2_error
            existing[-1]["constraint_context"] = stage2_constraints
        else:
            existing.append({
                "stage2_output": stage2_output,
                "stage2_hypothesis_tokens": hypothesis_tokens,
                "stage2_experiment_tokens": experiment_tokens,
                "stage2_total_latency": stage2_latency,
                "stage2_error": stage2_error,
                "constraint_context": constraint_context,
            })

        with open(LOG_FILE, "w") as f:
            json.dump(existing, f, indent=2)

        print(f"[Stage 2 logged to {LOG_FILE}]")


def log_run(
    input_text: str,
    output: str,
    latency: float,
    models_used: dict,
    token_usage: Optional[dict] = None,
    error: Optional[str] = None,
    gate_selection: Optional[str] = None,
    gate_timestamp: Optional[str] = None,
    context_updated: bool = False,
):
    RUNS_DIR.mkdir(exist_ok=True)

    existing = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r") as f:
            try:
                existing = json.load(f)
            except json.JSONDecodeError:
                existing = []

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "input_length": len(input_text),
        "output": output,
        "token_usage": token_usage,
        "latency_seconds": round(latency, 3),
        "models_used": models_used,
        "rubric_score": extract_rubric_score(output) if not error else None,
        "error": error,
        "gate_selection": gate_selection,
        "gate_timestamp": gate_timestamp,
        "context_updated": context_updated,
    }

    existing.append(entry)

    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def run_stage1(client: anthropic.Anthropic, raw_input: str, instructions: str, frameworks: str, active_constraints: str = "") -> tuple[str, Optional[dict], Optional[str]]:
    """Run bias detection + output generation. Returns (output, token_usage, error)."""
    output = ""
    token_usage: Optional[dict] = None
    error: Optional[str] = None

    try:
        bias_system = f"""You are a product discovery analyst running a silent bias detection pass.
Check the input against these 4 bias patterns and return a JSON object with your findings:
- PROXY_PAIN: Is there a stated request masking a deeper frustration?
- WORKAROUND: Has the user already solved this good enough?
- WRONG_METRIC: What is the user protecting with current behavior?
- RESEARCH_DECISION_GAP: Can you draw a direct line from this signal to a specific product decision?

Use these frameworks as context:
{frameworks}

Return only valid JSON in this shape:
{{"PROXY_PAIN": "...", "WORKAROUND": "...", "WRONG_METRIC": "...", "RESEARCH_DECISION_GAP": "..."}}"""

        bias_response = client.messages.create(
            model=MODEL_BIAS,
            max_tokens=1024,
            system=bias_system,
            messages=[{"role": "user", "content": raw_input}],
        )
        bias_findings = bias_response.content[0].text
        bias_tokens = {
            "input_tokens": bias_response.usage.input_tokens,
            "output_tokens": bias_response.usage.output_tokens,
        }

        constraints_block = ""
        if active_constraints:
            constraints_block = f"""
ACTIVE CONSTRAINTS:
{active_constraints}

Apply this two-tier structure to all signals, bias flags, and recommendations:

TIER 1 — WITHIN CONSTRAINTS:
Analysis and recommendations executable within active constraints.
Always include at least one Tier 1 solution.
These are the primary recommendations.

TIER 2 — BEYOND CONSTRAINTS:
Analysis that would be more valuable but requires lifting one or more constraints.
For each Tier 2 item include:
- Which constraint it conflicts with
- What lifting that constraint requires
- What this would unlock if pursued
- Specific trigger for when to revisit

Rules:
Never suppress a strategically important insight because of a constraint.
Surface it in Tier 2 instead.

When a signal points toward a constrained solution add a CONSTRAINT NOTE:
'Evidence suggests [solution] but [constraint] rules this out.
Constrained path is [Tier 1 alternative].'

For every recommendation explicitly address at least one of Hamilton Helmer's 7 Powers:
Scale economies, Network economies, Counter-positioning, Switching costs,
Branding, Cornered resource, Process power.

If none apply strongly to Tier 1 solutions state which power the solution is weakest
on and why that matters for defensibility.

If Tier 2 solutions have stronger 7 Powers scores than Tier 1 note this explicitly —
it signals that lifting the constraint produces a more defensible outcome.
"""

        output_system = f"""You are a product discovery analyst. Follow these instructions exactly:

{instructions}

Use these frameworks as context when analyzing signals:
{frameworks}
{constraints_block}
The following bias detection findings have already been identified (do not repeat this step):
{bias_findings}

After identifying bias flags and before generating any recommendations, run a fixability check.

## FIXABILITY CHECK

Assess the core problem on two dimensions:

DIMENSION 1 — GAP TYPE:

FIXABLE DISTANCE: The product direction is correct but delivery, activation, positioning, or execution is wrong. Optimization can close the gap. The current segment can benefit from this product if the right changes are made.

STRUCTURAL DIVIDE: The current segment structurally lacks what the product requires to deliver value. This could be:
- Capabilities they do not have
- Behaviors they cannot sustain
- Resources or scale they cannot reach
- A job that does not exist for them
No amount of optimization closes a structural divide.

DIMENSION 2 — EVIDENCE STRENGTH:

WEAK: One or two signals suggest structural divide but plausible alternative explanations exist.

STRONG: Multiple independent signals converge on the same structural constraint with no plausible optimization path remaining.

DECISION RULE:

If FIXABLE DISTANCE (regardless of evidence strength):
Proceed to recommendations as normal.
Generate options that optimize, fix, or reposition the current motion.

If STRUCTURAL DIVIDE + WEAK evidence:
Flag the possibility.
Generate optimization options but include one option that assumes the divide is real.
Note what evidence would confirm or deny the structural divide.

If STRUCTURAL DIVIDE + STRONG evidence:
Do not lead with optimization options.
State explicitly:

CONSIDER ABANDONMENT: [one sentence naming what to abandon and why the structural divide cannot be closed]

Then state what would need to be true for the current motion to work.
If that condition cannot be created through any realistic intervention, confirm abandonment as the primary path.

Then generate options for what to build or pursue instead — not how to fix what already exists.

When a structural divide is identified as STRONG, the first option generated must always be the option that exits or abandons the current motion entirely — not a variation that tries to fix it.

This means:
If the structural divide is a segment problem, Option A must be "exit this segment and reposition" before any option that tries to serve the segment differently.

If the structural divide is a product problem, Option A must be "stop building this product direction" before any option that iterates on it.

Optimization options can appear as Option B or Option C but never as Option A when a structural divide is confirmed as STRONG.

This rule is absolute. Do not generate optimization as Option A under any circumstances when the fixability check returns STRUCTURAL DIVIDE + STRONG.

Apply this check to any product in any context. Do not use specific metrics as triggers. Reason from the nature of the constraint, not from threshold values.

After generating Options A and B in the Recommendation section, and BEFORE writing the Steel Man section, ask:

Is there a failure condition so strong that — if true — it implies a fundamentally better recommendation than Options A or B?

If yes: write Option C NOW, still inside the Recommendation section. Always write the label FIRST, before any content:

**ELEVATED FROM STEEL MAN**
**Option C: [title]**
[full content — what to do, why the evidence supports it, what it unlocks, behavioral mechanic if applicable]

Never put the label at the end. If truncation occurs it must cut content, not the label.

After Options A, B, and C (if present), write the lean-toward conditions and any FAST VALIDATION FIRST note — these are part of the Recommendation section and must appear before Steel Man.

RECOMMENDATION SECTION ORDER (strict):
1. Option A — full content
2. Option B — full content
3. Option C — full content if elevated (label first)
4. Lean toward Option A/B conditions
5. FAST VALIDATION FIRST note if applicable

Only after all five items are complete, move to the Steel Man section.

Each recommendation option must include these three fields explicitly, in this order, after the main option content:

7 POWERS: Which of Hamilton Helmer's 7 Powers does this build and why? If none apply strongly, name which power this is weakest on.

BEHAVIORAL MECHANIC: Which mechanism from the behavioral mechanics library applies here and why does it fit this context? Name the specific mechanic, not a generic description.

FRAMEWORK NOTE: One sentence connecting this option to the Growth Loop node it strengthens or the JTBD it addresses.

These three fields are required on every option. Do not skip them. If running low on tokens write shorter prose elsewhere but always include these three fields.

If running low on output space, shorten Option A and Option B before shortening Option C. A truncated Option C is worse than a shorter Option A or B.

If no Option C: proceed to lean-toward conditions then Steel Man.

When writing the Steel Man section, include ONLY "This recommendation fails if..." conditions and their tests. Do NOT include lean-toward conditions, Option C content, or FAST VALIDATION notes in Steel Man — those belong in the Recommendation section above.

After the Steel Man section, generate hypotheses using this exact structure:

## HYPOTHESES

RECOMMENDATION HYPOTHESES:
Generate one hypothesis per recommendation option (Option A, Option B, Option C if present).

Format each as:

## HYPOTHESIS [A/B/C]
Testing: Option [A/B/C]
Core belief: [one falsifiable sentence]
If we're wrong: [specific invalidating signal]
Leverage: [HIGH/MEDIUM/LOW]
Risk: [HIGH/MEDIUM/LOW]
Priority: [RUN FIRST/RUN SECOND/RUN THIRD/DEPRIORITIZE]
Fastest test: [one specific cheap experiment]

FRAME-BREAKING HYPOTHESES:
Generate 1-2 hypotheses that challenge the entire diagnostic frame.

Format each as:

## FRAME-BREAKER [1/2]
What if: [alternative diagnosis]
Why this might be true: [evidence from input]
What it would mean: [how this changes everything]
Test: [fastest way to confirm or kill this]
Scoring: [VALIDATE BEFORE COMMITTING or LOW PRIOR]

Proceed to Step 2: Generate Output using these findings.

IMPORTANT: You MUST include the ## HYPOTHESES section at the end of your output. It is required. Do not end your response before generating all hypothesis blocks. If you are running low on space, shorten the analysis sections — never shorten or skip the hypotheses."""

        print("\nAnalyzing signals...\n")

        with client.messages.stream(
            model=MODEL_OUTPUT,
            max_tokens=24000,
            temperature=0,
            system=output_system,
            messages=[{"role": "user", "content": raw_input}],
        ) as stream:
            output_parts = []
            for text in stream.text_stream:
                print(text, end="", flush=True)
                output_parts.append(text)
            final_message = stream.get_final_message()

        output = "".join(output_parts)
        token_usage = {
            "bias_detection": bias_tokens,
            "output_generation": {
                "input_tokens": final_message.usage.input_tokens,
                "output_tokens": final_message.usage.output_tokens,
            },
        }

    except Exception as e:
        error = str(e)
        print(f"\nError: {error}", flush=True)

    return output, token_usage, error


def setup_company_context() -> None:
    """Prompt user to create company-context.md if it doesn't exist."""
    context_file = PROJECT_ROOT / "knowledge" / "company-context.md"

    if context_file.exists():
        content = load_file(context_file)
        # Extract first non-empty line under ## What We're Building
        building_match = re.search(
            r"## What We're Building\s*\n+(.+)", content
        )
        first_line = building_match.group(1).strip() if building_match else "context file found"
        print(f"Context loaded: {first_line}")
        return

    answer = input("No company context found. Set it up now? [Y/N]: ").strip().upper()
    if answer != "Y":
        return

    print()
    what = input(
        "What are you building and who is it for?\n(2-3 sentences): "
    ).strip()
    print()
    north_star = input(
        "What is your north star metric — the one\n"
        "behavior that matters most if users do it?: "
    ).strip()
    print()
    print(
        "Question 4: What are your biggest constraints right now? "
        "Describe in plain language what rules out certain solutions.\n\n"
        "Examples:\n"
        "'Two person team, no budget for paid ads, need signal in 3 weeks'\n"
        "'Can't change core product, existing users only, heavily regulated industry'\n"
        "'Solo founder, organic growth only, pre-revenue so need cheap experiments'\n\n"
        "Press Enter to skip."
    )
    constraint_raw = input("Constraints: ").strip()

    # Parse constraints via API if user provided input
    active_constraints_section = "None specified"
    if constraint_raw:
        try:
            extractor_client = anthropic.Anthropic()
            extract_response = extractor_client.messages.create(
                model=MODEL_BIAS,
                max_tokens=512,
                system="You are a structured data extractor.",
                messages=[{
                    "role": "user",
                    "content": (
                        "Extract constraints from this plain language description "
                        "into a JSON object:\n\n"
                        "{\n"
                        '  "team_size": ["solo","small","medium","large",null],\n'
                        '  "budget": ["none","under_1k","under_10k","funded",null],\n'
                        '  "time_pressure": ["days","weeks","months","none",null],\n'
                        '  "technical_capacity": ["none","limited","moderate","full",null],\n'
                        '  "acquisition_control": ["organic_only","some","full",null],\n'
                        '  "user_base": ["existing_only","can_acquire_new","both",null],\n'
                        '  "product_flexibility": ["locked","limited","flexible",null],\n'
                        '  "regulatory": ["high","some","free",null],\n'
                        '  "revenue_pressure": ["immediate","90_days","patient",null],\n'
                        '  "other": ["string or null"]\n'
                        "}\n\n"
                        "Only return valid JSON. Set unused fields to null.\n\n"
                        f"Input: {constraint_raw}"
                    ),
                }],
            )
            parsed = json.loads(extract_response.content[0].text)
            lines = [
                f"{k.replace('_', ' ').title()}: {v}"
                for k, v in parsed.items()
                if v is not None and v != "null"
            ]
            if lines:
                active_constraints_section = "\n".join(lines)
        except Exception:
            # Fall back to storing raw text if extraction or parsing fails
            active_constraints_section = constraint_raw

    timestamp = datetime.now(timezone.utc).isoformat()
    context_content = f"""# Company Context
Last updated: {timestamp}

## What We're Building
{what}

## North Star Metric
{north_star}

## Active Constraints
{active_constraints_section}

## Research History
"""

    context_file.parent.mkdir(parents=True, exist_ok=True)
    context_file.write_text(context_content)
    print("\nContext saved. You can update this anytime by deleting company-context.md\n")


def run():
    print("\nPM DISCOVERY OS")
    print("---------------\n")

    setup_company_context()

    # Main menu
    while True:
        print("\nWhat would you like to do?")
        print("[P] Process new signals (Stage 1 + 2)")
        print("[I] Interpret experiment results")
        print("[Q] Quit")
        menu_choice = input("\nSelect: ").strip().upper()
        if menu_choice in ("P", "I", "Q"):
            break
        print("Invalid selection. Enter P, I, or Q.")

    if menu_choice == "Q":
        return

    if menu_choice == "I":
        run_interpret()
        return

    # P — Process new signals
    instructions = load_file(WORKFLOW_FILE)
    frameworks = load_file(FRAMEWORKS_FILE)

    # Extract Active Constraints from company-context.md if present
    active_constraints = ""
    context_file = PROJECT_ROOT / "knowledge" / "company-context.md"
    if context_file.exists():
        context_content = context_file.read_text()
        constraints_match = re.search(
            r"## Active Constraints\s*\n(.*?)(?=\n##|\Z)",
            context_content,
            re.DOTALL,
        )
        if constraints_match:
            extracted = constraints_match.group(1).strip()
            if extracted and extracted != "None specified":
                active_constraints = extracted

    client = anthropic.Anthropic()

    # Verify API connection before running the full workflow
    try:
        client.messages.create(
            model=MODEL_BIAS,
            max_tokens=10,
            messages=[{"role": "user", "content": "ping"}],
        )
    except Exception as e:
        print(f"API connection check failed: {e}")
        return

    raw_input = get_multiline_input()
    if not raw_input.strip():
        print("No input provided. Exiting.")
        return

    while True:
        start = time.time()
        output, token_usage, error = run_stage1(client, raw_input, instructions, frameworks, active_constraints)
        latency = time.time() - start

        gate_selection: Optional[str] = None
        gate_timestamp: Optional[str] = None
        context_updated = False

        if not error:
            context_updated = update_context(raw_input, output)
            gate_selection, output = gate_prompt(output)
            gate_timestamp = datetime.now(timezone.utc).isoformat()

        print("\n")
        log_run(
            input_text=raw_input,
            output=output,
            latency=latency,
            models_used={"bias_detection": MODEL_BIAS, "output_generation": MODEL_OUTPUT},
            token_usage=token_usage,
            error=error,
            gate_selection=gate_selection,
            gate_timestamp=gate_timestamp,
            context_updated=context_updated,
        )
        print(f"[Logged to {LOG_FILE}]")

        if error or gate_selection == "Q":
            break
        elif gate_selection == "R":
            raw_input = get_multiline_input()
            if not raw_input.strip():
                print("No input provided. Exiting.")
                break
        elif gate_selection in ("Y", "E"):
            run_stage2(output)
            break
        elif gate_selection == "I":
            run_interpret()
            break


if __name__ == "__main__":
    run()
