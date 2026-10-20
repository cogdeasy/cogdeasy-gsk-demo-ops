"""Validates the repo's JSON data files against their JSON Schemas, plus cross-file checks.

demo-ops-validate            # every known data file
demo-ops-validate jira/backlog.json
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from collections.abc import Iterator, Sequence
from importlib import resources
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from demo_ops import REPO_ROOT

SCHEMAS: dict[str, str] = {
    "automations/automations.json": "automations.schema.json",
    "jira/seed.json": "jira-issues.schema.json",
    "jira/backlog.json": "jira-issues.schema.json",
    "jira/roles.json": "jira-issues.schema.json",
    "support-sim/reports.json": "support-reports.schema.json",
    "oncall-sim/alerts.json": "oncall-alerts.schema.json",
    "oncall-sim/expected.json": "oncall-expected.schema.json",
}
JIRA_KEY = re.compile(r"^[A-Z][A-Z0-9]+-[0-9]+$")


def load_schema(name: str) -> dict[str, Any]:
    text = resources.files("demo_ops.schemas").joinpath(name).read_text(encoding="utf-8")
    schema: dict[str, Any] = json.loads(text)
    return schema


def schema_errors(data: Any, schema: dict[str, Any]) -> Iterator[str]:
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        where = "/".join(str(p) for p in error.absolute_path) or "<root>"
        yield f"{where}: {error.message}"


def _duplicates(values: list[str]) -> list[str]:
    return sorted(v for v, n in Counter(values).items() if n > 1)


def check_automations(data: dict[str, Any], root: Path) -> Iterator[str]:
    automations = data["automations"]
    for name in _duplicates([a["name"] for a in automations]):
        yield f"duplicate automation name {name}"
    for a in automations:
        if "playbook" in a and not (root / a["playbook"]).is_file():
            yield f"{a['name']}: playbook {a['playbook']} does not exist"
        script = a["trigger"].get("script")
        if script and not (root / script.split()[0]).is_file():
            yield f"{a['name']}: trigger script {script.split()[0]} does not exist"


def check_issues(data: dict[str, Any], seen_refs: set[str] | None = None) -> Iterator[str]:
    issues = data["issues"]
    refs = [i["ref"] for i in issues]
    for ref in _duplicates(refs):
        yield f"duplicate ref {ref}"
    for key in _duplicates([i["key"] for i in issues if "key" in i]):
        yield f"duplicate key {key}"
    created: set[str] = set()
    for issue in issues:
        parent = issue.get("parent")
        if parent and parent not in created and not JIRA_KEY.fullmatch(parent):
            where = "later in the file" if parent in refs else "nowhere"
            yield f"{issue['ref']}: parent {parent} is defined {where}; seed creates in file order"
        trigger = issue.get("trigger_label")
        if trigger and trigger in issue["labels"]:
            yield f"{issue['ref']}: trigger label {trigger} must not be pre-applied"
        created.add(issue["ref"])
    known = set(refs) | {i["key"] for i in issues if "key" in i}
    for link in data.get("links", []):
        for end in ("from", "to"):
            target = link[end]
            if target not in known and not JIRA_KEY.fullmatch(target):
                yield f"link {link['from']} -> {link['to']}: unknown {end} {target}"
    if seen_refs is not None:
        seen_refs.update(refs)


def check_reports(data: dict[str, Any], seed_refs: set[str]) -> Iterator[str]:
    ids = [r["id"] for r in data["reports"]]
    for rid in _duplicates(ids):
        yield f"duplicate report id {rid}"
    for report in data["reports"]:
        dup = report["dup_of"]
        if dup is not None and dup not in ids and dup not in seed_refs:
            yield f"{report['id']}: dup_of {dup} is not a report id or jira/seed.json ref"


def check_alerts(alerts: dict[str, Any], expected: dict[str, Any] | None) -> Iterator[str]:
    ids = [a["id"] for a in alerts["alerts"]]
    for aid in _duplicates(ids):
        yield f"duplicate alert id {aid}"
    if expected is not None:
        answer_ids = [e["id"] for e in expected["expected"]]
        if sorted(answer_ids) != sorted(ids):
            yield f"expected.json ids {sorted(answer_ids)} do not match alerts {sorted(ids)}"


def validate(root: Path, only: Sequence[str] = ()) -> list[str]:
    """Return every problem as 'path: message'; empty means valid."""
    targets = list(only) or list(SCHEMAS)
    problems: list[str] = []
    loaded: dict[str, dict[str, Any]] = {}
    for rel in targets:
        if rel not in SCHEMAS:
            problems.append(f"{rel}: no schema registered (known: {', '.join(SCHEMAS)})")
            continue
        try:
            data = json.loads((root / rel).read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            problems.append(f"{rel}: {exc}")
            continue
        errors = list(schema_errors(data, load_schema(SCHEMAS[rel])))
        problems.extend(f"{rel}: {e}" for e in errors)
        if not errors:
            loaded[rel] = data

    def cross(rel: str, found: Iterator[str]) -> None:
        problems.extend(f"{rel}: {p}" for p in found)

    seed_refs: set[str] = set()
    if "jira/seed.json" not in loaded and "support-sim/reports.json" in loaded:
        seed_path = root / "jira" / "seed.json"
        seed_refs = {i["ref"] for i in json.loads(seed_path.read_text(encoding="utf-8"))["issues"]}
    for rel, data in loaded.items():
        if rel == "automations/automations.json":
            cross(rel, check_automations(data, root))
        elif rel.startswith("jira/"):
            cross(rel, check_issues(data, seed_refs if rel == "jira/seed.json" else None))
    if "support-sim/reports.json" in loaded:
        cross(
            "support-sim/reports.json", check_reports(loaded["support-sim/reports.json"], seed_refs)
        )
    if "oncall-sim/alerts.json" in loaded:
        expected = loaded.get("oncall-sim/expected.json")
        if expected is None and (root / "oncall-sim/expected.json").is_file():
            expected = json.loads((root / "oncall-sim/expected.json").read_text(encoding="utf-8"))
        cross("oncall-sim/alerts.json", check_alerts(loaded["oncall-sim/alerts.json"], expected))
    return problems


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="demo-ops-validate", description=__doc__.splitlines()[0])
    parser.add_argument("files", nargs="*", help="repo-relative data files (default: all)")
    parser.add_argument("--root", type=Path, default=REPO_ROOT, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    targets = [
        Path(f).resolve().relative_to(args.root.resolve()).as_posix() if Path(f).exists() else f
        for f in args.files
    ]
    problems = validate(args.root, targets)
    for problem in problems:
        print(problem)
    checked = len(targets or SCHEMAS)
    if problems:
        raise SystemExit(f"{len(problems)} problem(s) in {checked} file(s)")
    print(f"ok: {checked} file(s) valid")


if __name__ == "__main__":
    main()
