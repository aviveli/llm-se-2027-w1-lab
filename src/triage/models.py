"""Validated issue input and machine-readable triage output."""

from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class Issue(BaseModel):
    """Accept a single issue, including objects from the course snapshots."""

    model_config = ConfigDict(strict=True, str_strip_whitespace=True)

    repo: str | None = Field(default=None, min_length=1, max_length=200)
    number: int | None = Field(default=None, gt=0)
    title: str = Field(min_length=1, max_length=500)
    body: str = Field(default="", max_length=50_000)

    @model_validator(mode="before")
    @classmethod
    def reject_pull_requests(cls, value: object) -> object:
        if isinstance(value, dict):
            fields = cast(dict[object, object], value)
            if "pull_request" in fields:
                raise ValueError("Expected an issue, not a pull request")
            return fields
        return value

    @field_validator("body", mode="before")
    @classmethod
    def normalize_empty_body(cls, value: object) -> object:
        return "" if value is None else value


class Assessment(BaseModel):
    model_config = ConfigDict(
        extra="forbid", strict=True, str_strip_whitespace=True
    )

    issue_type: Literal[
        "bug", "enhancement", "documentation", "question", "meta", "unknown"
    ]
    summary: str = Field(min_length=1, max_length=1000)
    component: str | None = Field(min_length=1, max_length=200)
    priority: Literal["critical", "high", "normal", "low", "unknown"]
    rationale: str = Field(min_length=1, max_length=2000)
    missing_information: list[str] = Field(max_length=10)

    @field_validator("missing_information")
    @classmethod
    def validate_missing_information(cls, values: list[str]) -> list[str]:
        if any(not value.strip() or len(value) > 500 for value in values):
            raise ValueError("Missing-information entries must be 1-500 characters")
        return values


class TriageRecord(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    schema_version: Literal["1"] = "1"
    repo: str | None
    number: int | None
    assessment: Assessment
