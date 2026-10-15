import copy
import hashlib
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from zenithsync.artifacts import canonical_json, file_record, load_json
from zenithsync.review_coverage import audit_review_coverage


class ReviewCoverageTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.history = self.root / "history.json"
        self.review = self.root / "review.json"
        messages = [{"role": "user", "content": "task"},
                    {"role": "assistant", "content": "bounded result"}]
        self.history.write_bytes(canonical_json(messages))
        self.document = {
            "history": file_record(self.history), "message_count": 2,
            "message_bindings": {
                str(i): {"sha256": hashlib.sha256(canonical_json(m)).hexdigest(),
                         "size_bytes": len(canonical_json(m))}
                for i, m in enumerate(messages)},
            "review_sections": [{"start": 0, "end": 1, "finding": "Reviewed"}]}

    def audit(self, document=None):
        self.review.write_bytes(canonical_json(
            self.document if document is None else document))
        return audit_review_coverage(
            self.history, self.review,
            expected_history_sha256=self.document["history"]["sha256"],
            expected_review_sha256=file_record(self.review)["sha256"])

    def test_complete_coverage_does_not_approve_training(self):
        result = self.audit()
        self.assertTrue(result["structural_coverage_verified"])
        self.assertEqual(result["verified_message_count"], 2)
        self.assertFalse(result["training_approved"])

    def test_missing_extra_or_changed_message_binding_rejected(self):
        for mutation in ("missing", "extra", "changed"):
            d = copy.deepcopy(self.document)
            if mutation == "missing":
                del d["message_bindings"]["1"]
            elif mutation == "extra":
                d["message_bindings"]["2"] = d["message_bindings"]["1"]
            else:
                d["message_bindings"]["1"]["sha256"] = "0" * 64
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                self.audit(d)

    def test_range_gaps_overlaps_and_invalid_bounds_rejected(self):
        for spans in ([(0, 0)], [(0, 1), (1, 1)], [(-1, 1)],
                      [(0, 2)], [(1, 0)], [(False, 1)], []):
            d = copy.deepcopy(self.document)
            d["review_sections"] = [
                {"start": a, "end": b, "finding": "Reviewed"} for a, b in spans]
            with self.subTest(spans=spans), self.assertRaises(ValueError):
                self.audit(d)

    def test_changed_history_and_wrong_review_identity_rejected(self):
        self.audit()
        with self.assertRaises(ValueError):
            audit_review_coverage(self.history, self.review,
                expected_history_sha256=self.document["history"]["sha256"],
                expected_review_sha256="0" * 64)
        self.history.write_bytes(b"[]\n")
        with self.assertRaises(ValueError):
            self.audit()

    def test_invalid_count_empty_finding_and_delta_only_review_rejected(self):
        for key, value in (("message_count", True), ("message_count", 3),
                           ("review_sections", None),
                           ("review_sections", [{"start": 0, "end": 1,
                                                  "finding": " "}])):
            d = copy.deepcopy(self.document)
            d[key] = value
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.audit(d)

    def test_history_mutation_while_reading_review_rejected(self):
        def read_and_change(path):
            result = load_json(path)
            if path == self.review:
                self.history.write_bytes(b"[]\n")
            return result

        with patch("zenithsync.review_coverage.load_json", side_effect=read_and_change):
            with self.assertRaises(ValueError):
                self.audit()

    def test_oversized_input_rejected_before_hashing(self):
        with self.history.open("wb") as stream:
            stream.truncate(16 * 1024**2 + 1)
        with patch("zenithsync.review_coverage.file_record") as record:
            with self.assertRaises(ValueError):
                audit_review_coverage(self.history, self.review,
                    expected_history_sha256="0" * 64,
                    expected_review_sha256="0" * 64)
            record.assert_not_called()


if __name__ == "__main__":
    unittest.main()
