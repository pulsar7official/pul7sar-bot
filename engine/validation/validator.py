"""Validator subsystem: raw rendering request -> ValidatedPayload.

Per 02_ARCHITECTURE.md, Section 15, Step 1.1:

    Responsibility: Validate the raw incoming rendering request.
    Input:  Raw rendering request.
    Output: ValidatedPayload (immutable).
    Exception: ValidationError.
    Relationship with Pipeline: Invoked first by Pipeline with the raw
    request. Returns ValidatedPayload to Pipeline.
    Stateless. Does not modify the raw request; produces a new
    ValidatedPayload. Depends on no other subsystem.

And 02_ARCHITECTURE.md, Section 8 ("Architectural Constraints"):

    Validator must never:
        - resolve configuration
        - resolve assets
        - resolve fonts
        - create RenderContext
        - render pixels
        - know templates

And 02_ARCHITECTURE.md, Section 12 ("Exception Hierarchy"):

    ValidationError
        Raised by Validator when the raw incoming rendering request
        fails validation.
        Examples:
            - Missing required payload field.
            - Invalid render request.
            - Unsupported platform profile.
    ...
    Python built-in exceptions MUST NOT be exposed across subsystem
    boundaries. Engine subsystems MUST raise engine exceptions instead
    of raw built-in exceptions whenever possible.

The exact field-level schema of a rendering request (which fields are
"required", which platform profiles are "supported", etc.) is
explicitly left open by both frozen specifications -- neither
document names a single concrete field or platform value. Inventing
such business rules here would not be implementing the frozen
contract, it would be adding a contract that doesn't exist yet.

What *is* unambiguously required by the frozen contract is structural:
ValidatedPayload.data is declared as ``Mapping[str, Any]`` (see the
ValidatedPayload contract below, unchanged from Phase 1). A "raw
rendering request" that cannot be represented as such a mapping is not
a request the rest of the engine can consume, and Section 12's
"Invalid render request" example is exactly this case. Validator
therefore enforces only:

    - the raw request must not be ``None``
    - the raw request must be representable as a ``Mapping[str, Any]``
      (concretely: something ``dict(...)`` accepts, e.g. a Mapping or
      an iterable of key/value pairs)

Any failure to satisfy this is raised as ValidationError, with the
original built-in exception (if any) chained via ``from`` per Section
12's exception-chaining rule -- never left to escape as a raw
built-in exception. No other field, value, or "platform profile"
rule is invented beyond this structural minimum.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any, Mapping

from engine.core.exceptions import ValidationError


@dataclass(frozen=True)
class ValidatedPayload:
    """Immutable output of Validator.

    Contains data only -- no validation or rendering logic. The exact
    field schema of a validated rendering request is an implementation
    detail left open by the frozen specification; ``data`` holds the
    validated request fields as an immutable mapping, which is the
    smallest structure sufficient to satisfy the contract.
    """

    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "data", MappingProxyType(dict(self.data)))


class Validator:
    """Validates a raw incoming rendering request.

    Concrete implementation of the Validator contract (Architecture
    Section 15, Step 1.1; Rendering Specification Section 4).

    Stateless: holds no instance state and depends on no other
    subsystem -- ``validate`` is a pure function of its argument.
    Does not resolve configuration, assets, fonts, or templates; does
    not create RenderContext; does not render pixels (Architecture
    Section 8).
    """

    def validate(self, raw_request: Any) -> ValidatedPayload:
        """Validate ``raw_request`` and return a new ValidatedPayload.

        Does not modify ``raw_request``. Raises ValidationError if the
        request is missing or cannot be represented as the
        ``Mapping[str, Any]`` that ValidatedPayload requires (see
        module docstring for the precise, spec-derived scope of this
        check).
        """
        if raw_request is None:
            raise ValidationError(
                "Invalid render request: raw rendering request is missing "
                "(received None)."
            )

        try:
            data = dict(raw_request)
        except (TypeError, ValueError) as exc:
            raise ValidationError(
                "Invalid render request: raw rendering request must be "
                "representable as a mapping of field name to value "
                f"(got {type(raw_request).__name__!r})."
            ) from exc

        return ValidatedPayload(data=data)
