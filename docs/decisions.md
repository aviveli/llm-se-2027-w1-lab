# Unspecified decisions

The brief did not tell you everything. Every time you or your agent chose
something the brief did not specify, add a line here.

Examples of the kind of thing that counts: what fields the record has, what
happens to an issue with no clear type, how confident is confident enough,
what the output looks like when the model returns nothing usable.

You will need this list in W2, when we reconstruct the requirements this
build implicitly assumed. The comparison across the cohort is the lesson, so
write down what you actually decided, not what you think is the right answer.

---

- Scope is one issue to one triage record; no queue selection, GitHub writes, batch mode, or automatic assignment.
- Input is a UTF-8 JSON object from a file or stdin; title is required, body defaults to empty (including JSON null), and repo/positive issue number are optional provenance.
- Input accepts snapshot/GitHub metadata but drops everything except repo, number, title, and body before model inference; pull requests are rejected.
- Input title/body limits are 500/50,000 characters; oversized input fails rather than being silently truncated.
- Output is one JSON object with schema_version "1", repo, number, and a nested assessment; provenance is copied from input rather than generated.
- Assessment fields are issue_type, summary, component, priority, rationale, and missing_information; component is a repository-local subsystem name or null.
- Issue types follow the dataset vocabulary (bug, enhancement, documentation, question, meta), with unknown for insufficient evidence.
- Priority is an unverified impact estimate (critical/high/normal/low/unknown), not severity ground truth, a routing decision, or an SLA.
- Missing facts yield unknown/null plus clarification requests; no confidence number is exposed because model confidence is not calibrated.
- DSPy uses a typed JSON signature with temperature zero, a 30-second provider timeout, no provider retries, no response cache, and a 1,500-token output budget; adapters may make a repair request.
- Issue text is untrusted model input, never executable commands; the model has no tools, and prompt-injection resistance is not guaranteed by the prompt or schema.
- LLM_MODEL and provider credentials come from environment variables or .env without overriding existing environment variables.
- Invalid input exits 2; provider/configuration/response failures exit 1; errors go to stderr with no success-shaped fallback or stdout record.
- Model responses are runtime validated with closed enums and forbidden extra fields; provider errors are sanitized to avoid leaking credentials or issue text.
- Tests use mocked inference and require no credentials; live classification quality and prompt-injection resistance require separate evaluation.
