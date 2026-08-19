import unittest

from engine.entities.normalizer import create_entity_context, normalize_entity_key


class TestEntityNormalizer(unittest.TestCase):
    def test_aliases(self):
        self.assertEqual(normalize_entity_key("Chelsea FC"), "chelsea")
        self.assertEqual(normalize_entity_key("Real Madrid CF"), "real_madrid")
        self.assertEqual(normalize_entity_key("ريال مدريد"), "real_madrid")
        self.assertEqual(normalize_entity_key("Man Utd"), "manchester_united")

    def test_unknown_normalizes_deterministically(self):
        self.assertEqual(normalize_entity_key("Some Team"), "some_team")

    def test_none_and_blank(self):
        self.assertIsNone(normalize_entity_key(None))
        self.assertIsNone(normalize_entity_key("   "))

    def test_create_context(self):
        context = create_entity_context("Chelsea", kind="club")
        self.assertEqual(context.key, "chelsea")
        self.assertEqual(context.kind, "club")


if __name__ == "__main__":
    unittest.main()
