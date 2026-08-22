"""PUL7SAR Phase 18 story-intelligence domain.

This package sits before the deterministic rendering engine. It models story
meaning, factual safety, identity verification, editorial neutrality, visual
routing, concept direction, platform-aware scene specification, and generation
authorization without changing production publishing behavior.
"""

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
from engine.intelligence.generation_provider import (
    AuthorizedSceneGenerator, OriginalSceneProvider, OriginalSceneRequest, OriginalSceneResult,
)
from engine.intelligence.identity import (
    IdentityEvidence, IdentityRequirements, IdentityVerificationError, IdentityVerifier,
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
    "AuthorizationFailure", "AuthorizedSceneGenerator", "ClaimKind", "ConceptBrief",
    "ConceptConstraint", "ConceptDirectionError", "ConceptDirector", "EditorialNeutralityGate",
    "EditorialRole", "EntityCandidate", "EntityKind", "FactLock", "FactLockViolation",
    "GenerationAuthorization", "GenerationAuthorizer", "IdentityEvidence", "IdentityPlan",
    "IdentityRequirements", "IdentityStatus", "IdentityVerificationError", "IdentityVerifier",
    "LockedClaim", "LoserTreatment", "NeutralityDecision", "NeutralityViolation",
    "OriginalSceneProvider", "OriginalSceneRequest", "OriginalSceneResult",
    "OriginalSceneSpecification", "PerspectiveSentiment", "PlatformImageProfile",
    "PlatformProfileRegistry", "ProposedConcept", "ResultPerspectives", "ResultVisualTreatment",
    "SafeArea", "SceneIdentityReference", "SceneSpecCompiler", "Sentiment",
    "SentimentDecision", "SentimentEvidence", "SentimentProvider", "SentimentResolver",
    "SocialPlatform", "StoryAnalysisError", "StoryAnalyzer", "StoryBrief", "StoryClassification",
    "StoryClassifier", "StoryScope", "StoryType", "VisualFamily", "VisualFamilyRouter",
    "VisualIntent", "VisualRoute",
]
