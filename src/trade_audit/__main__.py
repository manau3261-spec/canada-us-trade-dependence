import argparse
import json
from pathlib import Path

from .acquire import acquire
from .pipeline import validate_run


def main() -> int:
    parser = argparse.ArgumentParser(description="Acquire and validate six public Statistics Canada tables.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root containing data/ and docs/")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("acquire", help="Retrieve and record a new official vintage")
    validate = commands.add_parser("validate", help="Validate an existing acquisition manifest offline")
    validate.add_argument("--manifest", type=Path, required=True, help="Path relative to the project root")
    commands.add_parser("run", help="Acquire then validate, recording partial failures")
    report = commands.add_parser("report", help="Regenerate the bilingual Markdown audit offline")
    report.add_argument("--validation", type=Path, required=True, help="Validation JSON path relative to project root")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "acquire":
        manifest = acquire(root)
        print(manifest.relative_to(root))
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        return int(any(item["status"] != "downloaded" for item in payload["sources"]))
    if args.command == "report":
        from .reports import render_reports
        render_reports(root, json.loads((root / args.validation).read_text(encoding="utf-8")))
        return 0
    manifest = acquire(root) if args.command == "run" else (root / args.manifest).resolve()
    path, result = validate_run(root, manifest)
    print(path.relative_to(root))
    if args.command == "run":
        from .reports import render_reports
        render_reports(root, result)
    return int(bool(result["blocking_issues"]))


if __name__ == "__main__":
    raise SystemExit(main())
