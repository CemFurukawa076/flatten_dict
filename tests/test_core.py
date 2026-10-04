import unittest

from flatten_dict import flatten, unflatten, MAX_DEPTH_EXCEEDED


class FlattenTests(unittest.TestCase):
    def test_flat_passthrough(self):
        data = {"a": 1, "b": 2}
        self.assertEqual(flatten(data), {"a": 1, "b": 2})

    def test_one_level_nested(self):
        data = {"a": {"b": 1, "c": 2}}
        self.assertEqual(flatten(data), {"a.b": 1, "a.c": 2})

    def test_multi_level_nested(self):
        data = {"a": {"b": {"c": {"d": 1}}}}
        self.assertEqual(flatten(data), {"a.b.c.d": 1})

    def test_custom_separator(self):
        data = {"a": {"b": 1}}
        self.assertEqual(flatten(data, sep="/"), {"a/b": 1})

    def test_lists_are_leaves(self):
        data = {"a": {"b": [1, 2, 3]}}
        self.assertEqual(flatten(data), {"a.b": [1, 2, 3]})

    def test_empty_nested_dict_preserved(self):
        data = {"a": {}}
        self.assertEqual(flatten(data), {"a": {}})

    def test_mixed_empty_and_values(self):
        data = {"a": {"b": {}}, "c": 1}
        self.assertEqual(flatten(data), {"a.b": {}, "c": 1})

    def test_rejects_non_mapping(self):
        with self.assertRaises(TypeError):
            flatten([("a", 1)])

    def test_rejects_excessive_depth(self):
        nested = {}
        cur = nested
        for _ in range(MAX_DEPTH_EXCEEDED + 5):
            cur["x"] = {}
            cur = cur["x"]
        with self.assertRaises(RecursionError):
            flatten(nested)


class UnflattenTests(unittest.TestCase):
    def test_simple_unflatten(self):
        flat = {"a.b": 1}
        self.assertEqual(unflatten(flat), {"a": {"b": 1}})

    def test_custom_separator_unflatten(self):
        flat = {"a/b": 1}
        self.assertEqual(unflatten(flat, sep="/"), {"a": {"b": 1}})

    def test_round_trip(self):
        original = {"a": {"b": {"c": 1}, "d": 2}, "e": 3}
        self.assertEqual(unflatten(flatten(original)), original)

    def test_round_trip_with_lists(self):
        original = {"a": {"b": [1, 2, 3]}}
        self.assertEqual(unflatten(flatten(original)), original)

    def test_round_trip_empty_dict(self):
        original = {"a": {}}
        self.assertEqual(unflatten(flatten(original)), original)

    def test_rejects_non_mapping(self):
        with self.assertRaises(TypeError):
            unflatten([("a", 1)])


if __name__ == "__main__":
    unittest.main()
