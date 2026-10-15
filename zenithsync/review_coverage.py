"""Verify full-message review bindings, without approving review conclusions."""

import hashlib
from pathlib import Path

from .artifacts import canonical_json, file_record, load_json
from .contracts import digest


def _read_bound(path, expected_sha256, limit):
    digest(expected_sha256)
    if path.stat().st_size > limit:
        raise ValueError("Review input exceeds byte limit")
    identity = file_record(path)
    if identity["sha256"] != expected_sha256:
        raise ValueError("Review input identity differs")
    value = load_json(path)
    if file_record(path) != identity:
        raise ValueError("Review input changed while decoding")
    return value, identity


def audit_review_coverage(history_path: Path, review_path: Path, *,
                          expected_history_sha256: str,
                          expected_review_sha256: str):
    """Check a native message list and its complete, range-based review record.

    Inputs must be quiescent files and digests must come from trusted evidence.
    This supports explicit full-review ranges, not inherited/delta reviews.
    Matching hashes do not prove truthful findings or authorize training.
    """
    history, history_identity = _read_bound(
        history_path, expected_history_sha256, 16 * 1024**2)
    review, review_identity = _read_bound(
        review_path, expected_review_sha256, 1024**2)
    if (not isinstance(history, list) or not 0 < len(history) <= 100000
            or any(not isinstance(message, dict) for message in history)):
        raise ValueError("Bounded nonempty native message list required")
    count = len(history)
    if (not isinstance(review, dict) or review.get("history") != history_identity
            or type(review.get("message_count")) is not int
            or review["message_count"] != count):
        raise ValueError("Review does not bind this complete history")
    bindings = review.get("message_bindings")
    if not isinstance(bindings, dict) or set(bindings) != {str(i) for i in range(count)}:
        raise ValueError("Exact per-message binding coverage required")
    for index, message in enumerate(history):
        payload = canonical_json(message)
        expected = {"sha256": hashlib.sha256(payload).hexdigest(),
                    "size_bytes": len(payload)}
        if bindings[str(index)] != expected:
            raise ValueError("Message binding differs")
    sections = review.get("review_sections")
    if not isinstance(sections, list) or not 0 < len(sections) <= count:
        raise ValueError("Explicit full-review sections required")
    covered = set()
    for section in sections:
        if (not isinstance(section, dict)
                or set(section) != {"start", "end", "finding"}
                or type(section["start"]) is not int
                or type(section["end"]) is not int
                or not 0 <= section["start"] <= section["end"] < count
                or not isinstance(section["finding"], str)
                or not section["finding"].strip()):
            raise ValueError("Invalid review section")
        indices = set(range(section["start"], section["end"] + 1))
        if covered.intersection(indices):
            raise ValueError("Overlapping review sections")
        covered.update(indices)
    if len(covered) != count:
        raise ValueError("Review sections omit messages")
    if (file_record(history_path) != history_identity
            or file_record(review_path) != review_identity):
        raise ValueError("Review inputs changed during verification")
    return {"schema_version": 1, "history": history_identity,
            "review": review_identity, "verified_message_count": count,
            "verified_section_count": len(sections),
            "structural_coverage_verified": True, "training_approved": False,
            "scope": "Identity and complete nonoverlapping coverage only; "
                     "review truth, task alignment and rights are not established."}
