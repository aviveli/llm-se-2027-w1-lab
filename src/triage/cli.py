"""Read one issue from a JSON file or stdin and print one JSON record."""

import argparse
import sys
from contextlib import redirect_stdout
from pathlib import Path

from dotenv import load_dotenv
from pydantic import ValidationError

from triage.extract import ExtractionError, triage_issue
from triage.models import Issue


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", nargs="?", default="-", help="JSON file, or - for stdin")
    args = parser.parse_args(argv)
    source: str = args.input
    try:
        text = (
            sys.stdin.read() if source == "-"
            else Path(source).read_text(encoding="utf-8-sig")
        )
        issue = Issue.model_validate_json(text)
    except (OSError, UnicodeError):
        print("error: Could not read the issue as UTF-8 JSON.", file=sys.stderr)
        return 2
    except ValidationError as exc:
        print(
            f"error: Invalid issue JSON: {exc.json(include_input=False, include_context=False)}",
            file=sys.stderr,
        )
        return 2

    load_dotenv()
    try:
        with redirect_stdout(sys.stderr):
            record = triage_issue(issue)
    except ExtractionError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(record.model_dump_json())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
