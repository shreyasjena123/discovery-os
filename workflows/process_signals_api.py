"""Non-interactive API wrapper for PM Discovery OS."""

import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import anthropic

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
WORKFLOW_FILE = SCRIPT_DIR / "process-signals.md"
FRAMEWORKS_FILE = PROJECT_ROOT / "knowledge" / "frameworks.md"
PRIORITIZATION_FILE = PROJECT_ROOT / "knowledge" / "prioritization-frameworks.md"
BEHAVIORAL_FILE = PROJECT_ROOT / "knowledge" / "behavioral-mechanics.md"
RUNS_DIR = PROJECT_ROOT / "runs"
LOG_FILE = RUNS_DIR / "log.json"

MODEL_BIAS = "claude-haiku-4-5-20251001"
MODEL_OUTPUT = "claude-sonnet-4-6"


def _load_file(path: Path) -> str:
    if path.exists():
        return path.read_text().strip()
    return ""


def _load_frameworks() -> str:
    parts = []

    frameworks = _load_file(FRAMEWORKS_FILE)
    if frameworks:
        parts.append(frameworks)

    prioritization = _load_file(PRIORITIZATION_FILE)
    if prioritization:
        parts.append(prioritization)

    behavioral = _load_file(BEHAVIORAL_FILE)
    if behavioral:
        parts.append(
            "Behavioral mechanics library — use this to name specific proven "
            "implementations when a recommendation identifies a retention or "
            f"engagement mechanism:\n{behavioral}"
        )

    return "\n\n".join(parts)


def _print_knowledge_status() -> None:
    files = {
        "frameworks.md": FRAMEWORKS_FILE,
        "prioritization-frameworks.md": PRIORITIZATION_FILE,
        "behavioral-mechanics.md": BEHAVIORAL_FILE,
        "process-signals.md": WORKFLOW_FILE,
    }
    print("[PM Discovery OS — Web API] Knowledge files:")
    for name, path in files.items():
        status = "✓" if path.exists() else "✗ MISSING"
        print(f"  {status}  {name}")


_print_knowledge_status()


def _append_log_entry(entry: dict) -> None:
    RUNS_DIR.mkdir(exist_ok=True)
    existing = []
    if LOG_FILE.exists():
        try:
            existing = json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            existing = []
    existing.append(entry)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def _update_last_log_entry(fields: dict) -> None:
    RUNS_DIR.mkdir(exist_ok=True)
    existing = []
    if LOG_FILE.exists():
        try:
            existing = json.loads(LOG_FILE.read_text())
        except json.JSONDecodeError:
            existing = []
    if existing:
        existing[-1].update(fields)
    else:
        existing.append(fields)
    with open(LOG_FILE, "w") as f:
        json.dump(existing, f, indent=2)


def run_api(signals: str, context: dict, api_key: str) -> dict:
    """Run Stage 1 analysis. Returns {output, token_usage, error}."""
    # Import run_stage1 from the CLI module
    import sys
    sys.path.insert(0, str(SCRIPT_DIR))
    from process_signals import run_stage1, extract_rubric_score

    active_constraints = context.get("constraints", "").strip()
    instructions = _load_file(WORKFLOW_FILE)
    frameworks = _load_frameworks()

    client = anthropic.Anthropic(api_key=api_key)

    start = time.time()
    output, token_usage, error = run_stage1(
        client, signals, instructions, frameworks, active_constraints
    )
    latency = round(time.time() - start, 3)

    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "web",
        "input_length": len(signals),
        "output": output,
        "token_usage": token_usage,
        "latency_seconds": latency,
        "models_used": {
            "bias_detection": MODEL_BIAS,
            "output_generation": MODEL_OUTPUT,
        },
        "rubric_score": extract_rubric_score(output) if not error else None,
        "error": error,
        "context": context,
    }
    _append_log_entry(entry)

    return {"output": output, "token_usage": token_usage, "error": error}


def run_stage2_api(
    stage1_output: str,
    selected_hypotheses: list,
    constraints: str,
    api_key: str,
) -> dict:
    """Run hypothesis generation + experiment design. Returns {hypotheses, experiments, error}."""
    client = anthropic.Anthropic(api_key=api_key)
    start = time.time()

    hypothesis_tokens: Optional[dict] = None
    experiment_tokens: Optional[dict] = None
    hypotheses = ""
    experiments = ""
    error: Optional[str] = None

    try:
        # --- Constraints block ---
        constraints_block = ""
        if constraints:
            constraints_block = (
                f"ACTIVE CONSTRAINTS:\n{constraints}\n\n"
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

        # --- Call 1: Hypothesis generation (Haiku) ---
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

        # --- Filter to selected hypotheses ---
        if selected_hypotheses:
            # Split on BOTH hypothesis headers and frame-breaker headers
            hyp_blocks = re.split(
                r"(?=(?:#{1,4}\s*)?(?:HYPOTHESIS\s+\[?[A-Za-z0-9]+\]?|FRAME-BREAKER\s+\[?\d+\]?))",
                hypotheses, flags=re.IGNORECASE
            )
            hyp_blocks = [b for b in hyp_blocks if b.strip()]
            selected_set = set(str(s).upper() for s in selected_hypotheses)
            # Normalise FB1/FB2 → "FB1" so they match what the frontend sends
            def block_id(block):
                m = re.match(r"(?:#{1,4}\s*)?HYPOTHESIS\s+\[?([A-Za-z0-9]+)\]?", block.strip(), re.IGNORECASE)
                if m:
                    return m.group(1).upper()
                m2 = re.match(r"(?:#{1,4}\s*)?FRAME-BREAKER\s+\[?(\d+)\]?", block.strip(), re.IGNORECASE)
                if m2:
                    return "FB" + m2.group(1)
                return None
            filtered = "\n\n".join(b for b in hyp_blocks if block_id(b) in selected_set)
            if filtered.strip():
                filtered_hypotheses = filtered
            else:
                filtered_hypotheses = hypotheses
        else:
            filtered_hypotheses = hypotheses

        # --- Build explicit hypothesis ID list for experiment prompt ---
        # Parse the IDs from the filtered hypotheses so the prompt can name them explicitly.
        import re as _re
        _hyp_id_hits = _re.findall(
            r"(?:HYPOTHESIS\s+\[?([A-Za-z0-9]+)\]?|FRAME-BREAKER\s+\[?(\d+)\]?)",
            filtered_hypotheses, _re.IGNORECASE
        )
        _hyp_ids = []
        for letter, num in _hyp_id_hits:
            if letter:
                _hyp_ids.append(letter.upper())
            elif num:
                _hyp_ids.append("FRAME-BREAKER " + num)
        _hyp_count = len(_hyp_ids)
        _hyp_list_str = ", ".join(_hyp_ids) if _hyp_ids else "the provided hypotheses"

        # --- Call 2: Experiment design (Sonnet, streaming) ---
        exp_system = (
            "You are a product discovery analyst.\n\n"
            f"You have been given exactly {_hyp_count} hypothesis/hypotheses to design "
            f"experiments for: {_hyp_list_str}.\n\n"
            f"You MUST output exactly {_hyp_count} experiment block(s) — one per hypothesis, "
            "in the same order as provided. Do not skip any hypothesis. Do not add extras.\n\n"
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
            f"CONSTRAINT CONTEXT: {constraints if constraints else 'No specific constraint'}\n"
            "When recommending experiment types, prioritize "
            "experiments that are feasible within this "
            "constraint. A small team cannot run a Wizard "
            "of Oz requiring 40+ hours of manual ops. "
            "A tight budget rules out paid prototype testing. "
            "Adjust recommendations accordingly and "
            "explicitly note if a recommended experiment "
            "requires more resources than the constraint allows.\n\n"
            "For each hypothesis output EXACTLY this structure with NO preamble:\n\n"
            "EXPERIMENT FOR HYPOTHESIS [X]:\n"
            "(use the exact hypothesis ID — letter for regular hypotheses, "
            "FRAME-BREAKER N for frame-breakers)\n"
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
            "[one sentence describing confirmed condition]\n\n"
            "---\n\n"
            "(repeat for each remaining hypothesis)"
        )

        exp_parts = []
        with client.messages.stream(
            model=MODEL_OUTPUT,
            max_tokens=6000,
            system=exp_system,
            messages=[{"role": "user", "content": filtered_hypotheses}],
        ) as stream:
            for text in stream.text_stream:
                exp_parts.append(text)
            exp_final = stream.get_final_message()

        experiments = "".join(exp_parts)
        experiment_tokens = {
            "input_tokens": exp_final.usage.input_tokens,
            "output_tokens": exp_final.usage.output_tokens,
        }

    except Exception as e:
        error = str(e)

    finally:
        latency = round(time.time() - start, 3)
        _update_last_log_entry({
            "stage2_output": hypotheses + "\n\n" + experiments,
            "stage2_hypothesis_tokens": hypothesis_tokens,
            "stage2_experiment_tokens": experiment_tokens,
            "stage2_total_latency": latency,
            "stage2_error": error,
            "constraint_context": constraints,
            "source": "web",
        })

    return {"hypotheses": hypotheses, "experiments": experiments, "error": error}
