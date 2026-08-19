import unittest
from dataclasses import FrozenInstanceError

from engine.entities.model import EntityContext


class TestEntityContext(unittest.TestCase):
    def test_optional_context(self):
        self.assertIsNone(EntityContext().key)

    def test_context_is_frozen(self):
        entity = EntityContext(key="chelsea")
        with self.assertRaises(FrozenInstanceError):
            entity.key = "liverpool"  # type: ignore[misc]

    def test_blank_key_rejected(self):
        with self.assertRaises(ValueError):
            EntityContext(key="   ")


if __name__ == "__main__":
    unittest.main()
