import unittest

from resolver.matcher import comparable, rank_results
from resolver.normalize import normalize_query


class ResolverTests(unittest.TestCase):
    def test_simplified_to_traditional(self):
        self.assertEqual(normalize_query("冻柠茶"), "凍檸茶")

    def test_remove_noise(self):
        self.assertEqual(normalize_query("凍檸茶幾多卡"), "凍檸茶")

    def test_rank_full_dish_before_ingredient(self):
        results = [
            {"name": "牛腩（配河粉）", "category": "配料"},
            {"name": "乾炒牛肉河", "category": "炒粉麵"},
            {"name": "牛丸（配河粉）", "category": "配料"},
        ]
        ranked = rank_results(results, "牛河")
        self.assertEqual(ranked[0]["name"], "乾炒牛肉河")

    def test_measurement_basis_guard(self):
        a = {"data_basis": "每碟", "unit_description": "每份"}
        b = {"data_basis": "每100g", "unit_description": "每100g/ml"}
        self.assertFalse(comparable(a, b))

    def test_same_basis_is_comparable(self):
        a = {"data_basis": "每碟", "unit_description": "每份"}
        b = {"data_basis": "每碟", "unit_description": "每份"}
        self.assertTrue(comparable(a, b))


if __name__ == "__main__":
    unittest.main()
