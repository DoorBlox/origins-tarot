"""Reproducible source-fidelity inventory for all 434 Rev2/Rev3 abilities.

Use:
    python -m tools.arcane_fidelity_report --format markdown
    python -m tools.arcane_fidelity_report --format json --output worklist.json

Categories are keyword triage labels, NOT verified technical feasibility.
The emitted per-ability \`missing\` text is the authored source disclosure.
Never infer real gameplay acceptance, mod support or release authorization.
"""
import argparse
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from arcane_rev3.powers import compile_powers  # noqa: E402

RULES = (
    ("team_targeting", r"ally|allies|teammat|enemy|friendly|neutral|player.target"),
    ("events_and_ai", r"\bai\b|aggro|event|on.hit|kill|right.click|mob|entity|projectile|retaliat"),
    ("world_and_blocks", r"terrain|block|zone|region|structure|weather|spawn|light|lectern|portal"),
    ("timing_and_cooldowns", r"cooldown|interval|tick|duration|timed|delay|window|every \d+"),
    ("visual_and_client", r"skin|model|client|hud|overlay|particle|outline|name|chat|disguise|morph"),
    ("resources_and_values", r"\bsin\b|resource|health|damage|exact|percent|stack|charge|heal|drain"),
    ("inventory_and_state", r"inventory|item|nbt|relog|death|source|save|drop|persist|book|potion"),
    ("installed_mod_api", r"\bmod\b|pehkui|skinshifter|remorphed|\bapi\b|fabric|kubejs"),
)
COMPILED_RULES = tuple(
    (label, re.compile(pattern, re.IGNORECASE)) for label, pattern in RULES
)


def categorize(missing: str) -> list[str]:
    labels = [label for label, pattern in COMPILED_RULES
              if pattern.search(missing)]
    return labels or ["other_unclassified"]


def build_inventory(root: Path = ROOT) -> dict:
    compiled, manifest, _ = compile_powers(Path(root))
    statuses = ("full", "partial", "blocked")
    counts = {
        "catalog": len(manifest),
        **{status: sum(row["status"] == status for row in manifest)
           for status in statuses},
    }
    if counts["catalog"] != 434 or counts["blocked"] != 0:
        raise AssertionError("Unexpected source catalog status: inspect build output")
    items = []
    for source in manifest:
        if source["status"] != "partial":
            continue
        ident = source["power_id"]
        if not ident or ident not in compiled or not source["missing"].strip():
            raise AssertionError(f"Partial power missing real code/disclosure: {ident}")
        items.append({
            "family": source["family"],
            "pathway": source["pathway"],
            "sequence": source["sequence"],
            "power_id": ident,
            "name": source["name"],
            "flag": source["flag"],
            "missing": source["missing"],
            "categories": categorize(source["missing"]),
        })
    items.sort(key=lambda x: (
        x["family"], x["pathway"], -x["sequence"], x["power_id"]))
    category_counts = {}
    for row in items:
        for category in row["categories"]:
            category_counts[category] = category_counts.get(category, 0) + 1
    return {
        "scope": "Arcane V2 Rev3 source only; NOT Minecraft gameplay tested",
        "classification": "Non-exclusive keyword triage, not feasibility or completion",
        "counts": counts,
        "category_counts": dict(sorted(category_counts.items())),
        "items": items,
    }


def to_markdown(report: dict) -> str:
    lines = [
        "# Arcane V2 Rev3 — fidelity worklist (generated)",
        "",
        "> Source-only worklist. No claim of gameplay or SMP readiness.",
        "> Categories are overlapping keyword triage, NOT engineering verdicts.",
        "",
        f"Definitions: {report['counts']['catalog']}; "
        f"source-full: {report['counts']['full']}; "
        f"source-partial: {report['counts']['partial']}; "
        f"blocked: {report['counts']['blocked']}.",
        "",
        "## Triage categories (overlap intentionally)",
        "",
    ]
    for category, total in report["category_counts"].items():
        lines.append(f"- {category}: {total}")
    lines.extend(["", "## All partial abilities and their declared missing mechanics", ""])
    for row in report["items"]:
        lines.extend([
            f"### {row['power_id']} — {row['name']}",
            f"Family: {row['family']} | Seq: {row['sequence']} | "
            f"Labels: {', '.join(row['categories'])}",
            "",
            row["missing"],
            "",
        ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--format", choices=("json", "markdown"),
                        default="markdown")
    parser.add_argument("--output", type=Path,
                        help="Output file (default: stdout)")
    args = parser.parse_args()
    report = build_inventory()
    result = (
        json.dumps(report, ensure_ascii=False, indent=2) + "\n"
        if args.format == "json"
        else to_markdown(report) + "\n"
    )
    if args.output:
        args.output.write_text(result, encoding="utf8")
    else:
        sys.stdout.write(result)


if __name__ == "__main__":
    main()
