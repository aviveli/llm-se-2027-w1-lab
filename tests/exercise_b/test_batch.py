from typing import Any

from triage_by_agent.router import find_duplicates, process_batch, route_raw


def raw(**kw: Any) -> dict[str, Any]:
    base: dict[str, Any] = dict(
        issue_number=1,
        repo="hono",
        issue_type="bug",
        component="middleware",
        severity="medium",
        has_reproduction_steps="true",
        confidence="0.9",
    )
    base.update(kw)
    return base


def issue(n: int, title: str) -> dict[str, Any]:
    return {"number": n, "title": title, "body": "x" * 40, "repo": "hono"}


def test_route_raw_maps_queue() -> None:
    assert route_raw(raw()).queue == "engineering"


def test_route_raw_critical_escalates() -> None:
    r = route_raw(raw(severity="critical"))
    assert r.escalate
    assert r.sla_hours == 4


def test_empty_batch() -> None:
    report = process_batch([], [])
    assert report.routings == []
    assert report.duplicate_pairs == []


def test_batch_routes_each_issue() -> None:
    report = process_batch([raw()], [issue(1, "a")])
    assert [r.queue for r in report.routings] == ["engineering"]


def test_batch_reports_no_duplicates_for_a_single_issue() -> None:
    report = process_batch([raw()], [issue(1, "cannot start the server")])
    assert report.duplicate_pairs == []


def test_batch_reports_similar_titles() -> None:
    issues = [
        issue(1, "Cannot start the server"),
        issue(2, "cannot start the server!"),
        issue(3, "Documentation for authentication"),
    ]
    report = process_batch([raw(issue_number=i["number"]) for i in issues], issues)
    assert len(report.routings) == 3
    assert report.duplicate_pairs == [(1, 2)]


def test_duplicate_detection_respects_threshold() -> None:
    issues = [
        issue(1, "Cannot start the server"),
        issue(2, "cannot start the server!"),
    ]
    assert find_duplicates(issues, threshold=0.99) == []
