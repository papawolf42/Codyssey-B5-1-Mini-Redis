"""FNV-1a 해시 함수 및 HashMap 단위 테스트."""

import unittest

from mini_redis.hash_map import fnv1a_32


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


if __name__ == "__main__":
    unittest.main()
