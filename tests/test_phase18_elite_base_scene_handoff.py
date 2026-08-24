import unittest

from engine.intelligence.elite_base_scene_handoff import EliteBaseSceneHandoffCompiler
from engine.intelligence.generation_package import GenerationPackage
from engine.intelligence.zero_cost_models import ImageQualityTier


def package(reserved=None, hybrid=True):
    return GenerationPackage(
        platform='instagram_feed',
        canvas='1080x1350',
        scene_prompt=(
            'Premium cinematic sports editorial atmosphere, one continuous physical scene, '
            'dramatic realistic lighting, clean negative space, no readable overlays.'
        ),
        negative_constraints=(),
        asset_ids=(),
        factual_constraints=('generic benchmark only',),
        metadata={
            'hybrid_base_scene_contract': hybrid,
            'reserved_base_scene_content': reserved if reserved is not None else (
                'all readable text',
                'all platform branding and wordmarks',
                'scores, dates, statistics and exact numbers',
                'team, club and competition marks',
            ),
            'base_scene_overlay_policy': 'no_brand_or_editorial_overlays_in_ai_scene',
            'composition_grammar': 'single_continuous_scene',
        },
    )


class EliteBaseSceneHandoffTests(unittest.TestCase):
    def test_qwen_elite_handoff_is_portable_but_execution_blocked_until_floor_is_proven(self):
        handoff = EliteBaseSceneHandoffCompiler().compile(
            package=package(),
            seed=2512,
            request_id='elite-base-001',
        )
        self.assertEqual(handoff.contract, 'pul7sar-elite-base-scene-handoff-v1')
        self.assertEqual(handoff.quality_decision.selected_tier, ImageQualityTier.ELITE)
        self.assertEqual(handoff.request.model_id, 'Qwen/Qwen-Image-2512')
        self.assertTrue(handoff.request.metadata['portable_handoff'])
        self.assertTrue(handoff.quality_decision.portable_only)
        self.assertFalse(handoff.execution_authorized)
        self.assertFalse(handoff.publication_ready)
        self.assertFalse(handoff.generator_owns_readable_text)
        self.assertFalse(handoff.generator_owns_brand)
        self.assertFalse(handoff.generator_owns_exact_values)
        self.assertFalse(handoff.generator_owns_entity_marks)
        self.assertEqual(len(handoff.prompt_sha256), 64)

    def test_missing_hybrid_contract_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'REQUIRES_HYBRID'):
            EliteBaseSceneHandoffCompiler().compile(package=package(hybrid=False), seed=1, request_id='bad')

    def test_missing_exact_layer_reservation_is_rejected(self):
        incomplete = (
            'all readable text',
            'all platform branding and wordmarks',
            'team, club and competition marks',
        )
        with self.assertRaisesRegex(ValueError, 'exact numbers'):
            EliteBaseSceneHandoffCompiler().compile(package=package(incomplete), seed=1, request_id='bad')

    def test_protected_platform_name_in_prompt_is_rejected(self):
        bad = GenerationPackage(
            platform='instagram_feed', canvas='1080x1350',
            scene_prompt='PUL7SAR cinematic scene', negative_constraints=(), asset_ids=(), factual_constraints=(),
            metadata={
                'hybrid_base_scene_contract': True,
                'reserved_base_scene_content': (
                    'all readable text', 'all platform branding and wordmarks',
                    'scores, dates, statistics and exact numbers', 'team, club and competition marks',
                ),
            },
        )
        with self.assertRaisesRegex(ValueError, 'LEAKED_PROTECTED_BRAND'):
            EliteBaseSceneHandoffCompiler().compile(package=bad, seed=1, request_id='bad')


if __name__ == '__main__':
    unittest.main()
