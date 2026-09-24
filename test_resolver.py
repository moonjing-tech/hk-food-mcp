import unittest

from resolver.aliases import resolve_alias
from resolver.matcher import build_search_terms
from resolver.normalize import normalize_query


class ResolverTests(unittest.TestCase):
    def test_simplified_to_hong_kong_traditional(self):
        self.assertEqual(normalize_query("冻柠茶"), "凍檸茶")

    def test_remove_question_noise(self):
        self.assertEqual(normalize_query("凍檸茶幾多卡？"), "凍檸茶")

    def test_alias(self):
        self.assertEqual(resolve_alias("凍檸"), "凍檸茶")

    def test_ambiguous_term_is_not_forced(self):
        self.assertEqual(resolve_alias("牛河"), "牛河")

    def test_search_terms(self):
        terms = build_search_terms("冻柠茶几多卡")
        self.assertIn("凍檸茶", terms)


if __name__ == "__main__":
    unittest.main()
