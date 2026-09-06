import unittest

from engine.intelligence.classification import (
    EntityCandidate,
    EntityKind,
    StoryClassifier,
    StoryScope,
    StoryType,
)
from engine.intelligence.models import Sentiment, StoryBrief
from engine.intelligence.visual_router import VisualFamily, VisualFamilyRouter


class StoryClassificationRouterTests(unittest.TestCase):
    def setUp(self):
        self.classifier = StoryClassifier()
        self.router = VisualFamilyRouter()

    def test_general_multi_league_story_uses_brand_world(self):
        brief = StoryBrief(
            headline="Europe's major leagues are almost back",
            summary="A new season brings major stories across the continent.",
            sport="football",
            sentiment=Sentiment.ANTICIPATORY,
        )
        classification = self.classifier.classify(story_type="general")
        self.assertEqual(classification.scope, StoryScope.GENERAL)
        route = self.router.route(brief, classification)
        self.assertEqual(route.family, VisualFamily.GENERAL_WORLD)
        intent = self.router.to_intent(brief, classification)
        self.assertEqual(intent.color_strategy, "brand_red")
        self.assertIsNone(intent.hero_entity)

    def test_result_routes_through_neutrality_gate(self):
        team = EntityCandidate("Arsenal", EntityKind.CLUB, confidence=1.0)
        classification = self.classifier.classify(
            story_type="result", entity_candidates=(team,)
        )
        brief = StoryBrief(
            headline="Arsenal win",
            summary="Arsenal take the points.",
            sport="football",
            story_type="result",
            primary_entity="Arsenal",
            sentiment=Sentiment.POSITIVE,
        )
        route = self.router.route(brief, classification)
        self.assertEqual(route.family, VisualFamily.RESULTS)
        self.assertTrue(route.requires_neutrality_gate)

    def test_transfer_route_does_not_claim_completed_signing(self):
        player = EntityCandidate("Alberto Alvarez", EntityKind.PERSON, confidence=0.8)
        classification = self.classifier.classify(
            story_type="transfer", entity_candidates=(player,)
        )
        brief = StoryBrief(
            headline="Arsenal approach Alberto Alvarez",
            summary="Talks are progressing.",
            sport="football",
            story_type="transfer",
            primary_entity="Alberto Alvarez",
            event_status="approach",
            sentiment=Sentiment.ANTICIPATORY,
        )
        route = self.router.route(brief, classification)
        self.assertEqual(route.family, VisualFamily.TRANSFERS)
        self.assertIn("without implying an unverified signing", route.concept)

    def test_player_story_requires_identity_gate(self):
        person = EntityCandidate("Sam Hickey", EntityKind.PERSON, confidence=0.9)
        classification = self.classifier.classify(
            story_type="player_story", entity_candidates=(person,)
        )
        brief = StoryBrief(
            headline="Sam Hickey is a rising British prospect",
            summary="The Scottish middleweight continues his development.",
            sport="boxing",
            story_type="player_story",
            primary_entity="Sam Hickey",
            sentiment=Sentiment.POSITIVE,
        )
        route = self.router.route(brief, classification)
        self.assertEqual(route.family, VisualFamily.PLAYER_STORIES)
        self.assertTrue(route.requires_identity_gate)

    def test_general_scope_rejects_hidden_entity_candidates(self):
        with self.assertRaises(ValueError):
            from engine.intelligence.classification import StoryClassification
            StoryClassification(
                story_type=StoryType.GENERAL,
                scope=StoryScope.GENERAL,
                entity_candidates=(
                    EntityCandidate("Hidden Club", EntityKind.CLUB, confidence=0.5),
                ),
            )


if __name__ == "__main__":
    unittest.main()
