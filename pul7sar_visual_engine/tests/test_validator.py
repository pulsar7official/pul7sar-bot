"""Tests for the concrete Validator (engine.validation.validator).

Scope: Validator only, per Architecture Section 15 Step 1.1 and
Rendering Specification Section 4. Does not test ConfigurationResolver,
AssetResolver, FontResolver, Template, Renderer, Canvas,
QualityVerifier, Exporter, or Pipeline -- those are out of scope for
this session.

Written against the stdlib ``unittest`` module (no third-party test
runner required/available in this environment).
"""

from __future__ import annotations

import unittest
from types import MappingProxyType

from engine.core.exceptions import ValidationError, VisualEngineError
from engine.validation.validator import ValidatedPayload, Validator


class TestValidatedPayloadContract(unittest.TestCase):
    """The ValidatedPayload data contract itself must remain unchanged
    from Phase 1 (frozen unless the specifications require a change --
    they do not)."""

    def test_default_data_is_empty_mapping(self) -> None:
        payload = ValidatedPayload()
        self.assertEqual(dict(payload.data), {})

    def test_data_is_immutable_mapping_proxy(self) -> None:
        payload = ValidatedPayload(data={"a": 1})
        self.assertIsInstance(payload.data, MappingProxyType)
        with self.assertRaises(TypeError):
            payload.data["a"] = 2  # type: ignore[index]

    def test_payload_itself_is_frozen(self) -> None:
        payload = ValidatedPayload(data={"a": 1})
        with self.assertRaises(Exception):
            payload.data = {"b": 2}  # type: ignore[misc]


class TestValidatorSuccess(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = Validator()

    def test_validate_returns_validated_payload(self) -> None:
        result = self.validator.validate({"sport": "football", "template": "matchday"})
        self.assertIsInstance(result, ValidatedPayload)
        self.assertEqual(
            dict(result.data), {"sport": "football", "template": "matchday"}
        )

    def test_validate_accepts_empty_mapping(self) -> None:
        result = self.validator.validate({})
        self.assertEqual(dict(result.data), {})

    def test_validate_accepts_iterable_of_pairs(self) -> None:
        result = self.validator.validate([("a", 1), ("b", 2)])
        self.assertEqual(dict(result.data), {"a": 1, "b": 2})

    def test_validate_does_not_modify_raw_request(self) -> None:
        raw_request = {"sport": "football"}
        raw_request_copy = dict(raw_request)
        self.validator.validate(raw_request)
        self.assertEqual(raw_request, raw_request_copy)

    def test_validate_result_is_independent_of_raw_request_mutation(self) -> None:
        raw_request = {"sport": "football"}
        result = self.validator.validate(raw_request)
        raw_request["sport"] = "basketball"
        self.assertEqual(result.data["sport"], "football")

    def test_validate_is_stateless_across_calls(self) -> None:
        first = self.validator.validate({"a": 1})
        second = self.validator.validate({"b": 2})
        self.assertEqual(dict(first.data), {"a": 1})
        self.assertEqual(dict(second.data), {"b": 2})


class TestValidatorFailure(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = Validator()

    def test_validate_none_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.validator.validate(None)

    def test_validate_non_mapping_raises_validation_error(self) -> None:
        with self.assertRaises(ValidationError):
            self.validator.validate(12345)

    def test_validate_non_mapping_string_raises_validation_error(self) -> None:
        # A string is iterable but not a sequence of key/value pairs.
        with self.assertRaises(ValidationError):
            self.validator.validate("not-a-request")

    def test_validation_error_is_a_visual_engine_error(self) -> None:
        with self.assertRaises(VisualEngineError):
            self.validator.validate(None)

    def test_validation_error_chains_original_exception(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            self.validator.validate(12345)
        self.assertIsNotNone(ctx.exception.__cause__)

    def test_no_builtin_exception_escapes(self) -> None:
        try:
            self.validator.validate(12345)
        except ValidationError:
            pass
        except Exception as exc:  # pragma: no cover - defensive
            self.fail(f"A raw built-in exception escaped Validator: {exc!r}")


if __name__ == "__main__":
    unittest.main()
