"""Phase 1 tests: exception inheritance.

Verifies 02_ARCHITECTURE.md, Section 12 (Exception Hierarchy).
"""

import pytest

from engine.core.exceptions import (
    AssetError,
    ConfigurationError,
    ExportError,
    FontError,
    QualityVerificationError,
    RenderingError,
    TemplateError,
    ValidationError,
    VisualEngineError,
)

ALL_SUBCLASSES = [
    ValidationError,
    ConfigurationError,
    AssetError,
    FontError,
    TemplateError,
    RenderingError,
    QualityVerificationError,
    ExportError,
]


@pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
def test_every_subclass_inherits_from_visual_engine_error(exc_cls):
    assert issubclass(exc_cls, VisualEngineError)


@pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
def test_every_subclass_is_a_direct_child_of_visual_engine_error(exc_cls):
    # Direct child, not a grandchild through another engine exception.
    assert exc_cls.__bases__ == (VisualEngineError,)


def test_visual_engine_error_inherits_from_exception():
    assert issubclass(VisualEngineError, Exception)


def test_quality_verification_error_is_sibling_of_rendering_and_export_error():
    # Sibling, not a subtype of either (Architecture Section 12).
    assert not issubclass(QualityVerificationError, RenderingError)
    assert not issubclass(QualityVerificationError, ExportError)
    assert not issubclass(RenderingError, QualityVerificationError)
    assert not issubclass(ExportError, QualityVerificationError)


def test_no_two_subclasses_are_related_to_each_other():
    for a in ALL_SUBCLASSES:
        for b in ALL_SUBCLASSES:
            if a is b:
                continue
            assert not issubclass(a, b), f"{a.__name__} must not subclass {b.__name__}"


def test_exceptions_carry_a_human_readable_message():
    err = ValidationError("missing required field")
    assert str(err) == "missing required field"
