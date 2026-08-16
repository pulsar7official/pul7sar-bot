"""Template System for the PUL7SAR Visual Engine.

This package provides the template infrastructure:
    - BaseTemplate: Abstract base class for all templates
    - TemplateRegistry: Registry for template classes
    - TemplateResolver: Resolves template classes from requests
"""

from engine.templates.base import BaseTemplate
from engine.templates.registry import TemplateRegistry
from engine.templates.resolver import TemplateResolver

__all__ = [
    "BaseTemplate",
    "TemplateRegistry",
    "TemplateResolver",
]
