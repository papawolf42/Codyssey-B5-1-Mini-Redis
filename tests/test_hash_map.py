"""FNV-1a 해시 함수 및 HashMap 단위 테스트."""

import unittest

from mini_redis.hash_map import HashMap, fnv1a_32


class TestFnv1a32(unittest.TestCase):
    """FNV-1a 32비트 해시 함수의 표준 벡터와 일관성을 검증한다."""

    def test_standard_vectors(self):
        self.assertEqual(fnv1a_32(""), 0x811C9DC5)
        self.assertEqual(fnv1a_32("a"), 0xE40C292C)
        self.assertEqual(fnv1a_32("foobar"), 0xBF9CF968)

    def test_deterministic_and_utf8_range(self):
        h1 = fnv1a_32("한글:키")
        h2 = fnv1a_32("한글:키")
        self.assertEqual(h1, h2)
        self.assertTrue(0 <= h1 <= 0xFFFFFFFF)


class TestHashMap(unittest.TestCase):
    """체이닝 해시맵의 기본 저장, 조회, 충돌 처리 동작을 검증한다."""

    def test_put_get_and_missing(self):
        hm = HashMap()
        self.assertIsNone(hm.get("missing"))
        self.assertFalse(hm.contains("missing"))

        hm.put("a", 1)
        hm.put("b", "two")
        self.assertEqual(hm.get("a"), 1)
        self.assertEqual(hm.get("b"), "two")
        self.assertTrue(hm.contains("a"))
        self.assertEqual(hm.size(), 2)

    def test_put_overwrite_keeps_size(self):
        hm = HashMap()
        hm.put("a", 1)
        hm.put("a", 99)

        self.assertEqual(hm.get("a"), 99)
        self.assertEqual(hm.size(), 1)

    def test_keys_returns_all_keys(self):
        hm = HashMap()
        hm.put("c", 3)
        hm.put("a", 1)
        hm.put("b", 2)

        self.assertEqual(sorted(hm.keys()), ["a", "b", "c"])

    def test_collision_chaining(self):
        hm = HashMap(capacity=8)
        self.assertEqual(fnv1a_32("k0") % 8, fnv1a_32("k8") % 8)
        hm.put("k0", "v0")
        hm.put("k8", "v8")

        self.assertEqual(hm.get("k0"), "v0")
        self.assertEqual(hm.get("k8"), "v8")
        self.assertEqual(hm.size(), 2)

    def test_put_and_get_many(self):
        hm = HashMap()
        for i in range(100):
            hm.put("key:" + str(i), i)

        self.assertEqual(hm.capacity, 256)
        self.assertEqual(hm.size(), 100)
        for i in range(100):
            self.assertEqual(hm.get("key:" + str(i)), i)

    def test_resize_only_above_three_quarters(self):
        hm = HashMap(capacity=4)
        hm.put("a", 1)
        hm.put("b", 2)
        hm.put("c", 3)
        self.assertEqual(hm.capacity, 4)

        hm.put("a", 10)
        self.assertEqual(hm.capacity, 4)
        self.assertEqual(hm.size(), 3)

        hm.put("d", 4)
        self.assertEqual(hm.capacity, 8)
        self.assertEqual(hm.size(), 4)
        for key, value in (("a", 10), ("b", 2), ("c", 3), ("d", 4)):
            self.assertEqual(hm.get(key), value)

        self.assertTrue(hm.remove("c"))
        self.assertIsNone(hm.get("c"))
        self.assertEqual(hm.size(), 3)

    def test_remove_existing_and_missing(self):
        hm = HashMap()
        self.assertFalse(hm.remove("missing"))

        hm.put("a", 1)
        self.assertTrue(hm.remove("a"))
        self.assertFalse(hm.remove("a"))
        self.assertIsNone(hm.get("a"))
        self.assertFalse(hm.contains("a"))
        self.assertEqual(hm.size(), 0)

    def test_remove_in_collision_bucket(self):
        hm = HashMap(capacity=8)
        hm.put("k0", "v0")
        hm.put("k8", "v8")

        self.assertTrue(hm.remove("k0"))
        self.assertIsNone(hm.get("k0"))
        self.assertEqual(hm.get("k8"), "v8")
        self.assertEqual(hm.size(), 1)

    def test_remove_half_of_many(self):
        hm = HashMap()
        for i in range(100):
            hm.put("key:" + str(i), i)

        for i in range(0, 100, 2):
            self.assertTrue(hm.remove("key:" + str(i)))

        self.assertEqual(hm.size(), 50)
        for i in range(100):
            expected = None if i % 2 == 0 else i
            self.assertEqual(hm.get("key:" + str(i)), expected)


if __name__ == "__main__":
    unittest.main()
