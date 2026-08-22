"""PUL7SAR Phase 18 story-intelligence domain.

This package sits before the deterministic rendering engine. It models story
meaning, factual safety, identity verification, editorial neutrality, visual
routing, concept direction, platform-aware scene specification, asset/layout
safety, generation packaging, and authorization without changing production
publishing behavior.
"""

from engine.intelligence.assets import AssetBundle, AssetReference, AssetRole, AssetTreatment
from engine.intelligence.batch_scene import MultiPlatformSceneCompiler, PlatformScenePackage
from engine.intelligence.classification import (
    EntityCandidate, EntityKind, StoryClassification, StoryClassifier, StoryScope, StoryType,
)
from engine.intelligence.concept_director import (
    ConceptBrief, ConceptConstraint, ConceptDirectionError, ConceptDirector, ProposedConcept,
)
from engine.intelligence.fact_lock import FactLock, FactLockViolation
from engine.intelligence.generation_authorization import (
    AuthorizationFailure, GenerationAuthorization, GenerationAuthorizer,
)
from engine.intelligence.generation_package import GenerationPackage, GenerationPackageCompiler
from engine.intelligence.generation_provider import (
    AuthorizedSceneGenerator, OriginalSceneProvider, OriginalSceneRequest, OriginalSceneResult,
)
from engine.intelligence.identity import (
    IdentityEvidence, IdentityRequirements, IdentityVerificationError, IdentityVerifier,
)
from engine.intelligence.layout_safety import (
    ElementBox, LayoutRole, LayoutSafetyDecision, PlatformLayoutSafetyGate,
)
from engine.intelligence.models import (
    ClaimKind, IdentityPlan, IdentityStatus, LockedClaim, Sentiment, StoryBrief, VisualIntent,
)
from engine.intelligence.neutrality import (
    EditorialNeutralityGate, LoserTreatment, NeutralityDecision, NeutralityViolation,
    ResultVisualTreatment,
)
from engine.intelligence.perspective import EditorialRole, PerspectiveSentiment, ResultPerspectives
from engine.intelligence.platform_profiles import (
    PlatformImageProfile, PlatformProfileRegistry, SafeArea, SocialPlatform,
)
from engine.intelligence.scene_spec import (
    OriginalSceneSpecification, SceneIdentityReference, SceneSpecCompiler,
)
from engine.intelligence.sentiment import (
    SentimentDecision, SentimentEvidence, SentimentProvider, SentimentResolver,
)
from engine.intelligence.story_analyzer import StoryAnalysisError, StoryAnalyzer
from engine.intelligence.visual_router import VisualFamily, VisualFamilyRouter, VisualRoute

__all__ = [
    "AssetBundle", "AssetReference", "AssetRole", "AssetTreatment", "AuthorizationFailure",
    "AuthorizedSceneGenerator", "ClaimKind", "ConceptBrief", "ConceptConstraint",
    "ConceptDirectionError", "ConceptDirector", "EditorialNeutralityGate", "EditorialRole",
    "ElementBox", "EntityCandidate", "EntityKind", "FactLock", "FactLockViolation",
    "GenerationAuthorization", "GenerationAuthorizer", "GenerationPackage",
    "GenerationPackageCompiler", "IdentityEvidence", "IdentityPlan", "IdentityRequirements",
    "IdentityStatus", "IdentityVerificationError", "IdentityVerifier", "LayoutRole",
    "LayoutSafetyDecision", "LockedClaim", "LoserTreatment", "MultiPlatformSceneCompiler",
    "NeutralityDecision", "NeutralityViolation", "OriginalSceneProvider", "OriginalSceneRequest",
    "OriginalSceneResult", "OriginalSceneSpecification", "PerspectiveSentiment",
    "PlatformImageProfile", "PlatformLayoutSafetyGate", "PlatformProfileRegistry",
    "PlatformScenePackage", "ProposedConcept", "ResultPerspectives", "ResultVisualTreatment",
    "SafeArea", "SceneIdentityReference", "SceneSpecCompiler", "Sentiment", "SentimentDecision",
    "SentimentEvidence", "SentimentProvider", "SentimentResolver", "SocialPlatform",
    "StoryAnalysisError", "StoryAnalyzer", "StoryBrief", "StoryClassification",
    "StoryClassifier", "StoryScope", "StoryType", "VisualFamily", "VisualFamilyRouter",
    "VisualIntent", "VisualRoute",
]
