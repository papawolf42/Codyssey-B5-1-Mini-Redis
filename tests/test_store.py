"""Mini Redis의 문자열 저장과 최근 사용 순서를 검증한다."""

import unittest

from mini_redis.store import MiniRedis


def _lru_keys(store):
    return [node.data for node in store._lru]


class TestMiniRedis(unittest.TestCase):
    def test_set_and_get(self):
        store = MiniRedis()
        store.set("msg", "hello")

        self.assertEqual(store.get("msg"), "hello")
        self.assertEqual(_lru_keys(store), ["msg"])

    def test_get_missing_leaves_lru_order(self):
        store = MiniRedis()
        store.set("a", "first")
        store.set("b", "second")

        self.assertIsNone(store.get("missing"))
        self.assertEqual(_lru_keys(store), ["b", "a"])

    def test_set_overwrites_value_and_moves_key_to_front(self):
        store = MiniRedis()
        store.set("a", "old")
        store.set("b", "second")
        store.set("a", "new")

        self.assertEqual(_lru_keys(store), ["a", "b"])
        self.assertEqual(store.get("a"), "new")

    def test_get_moves_existing_key_to_front(self):
        store = MiniRedis()
        store.set("a", "first")
        store.set("b", "second")

        self.assertEqual(_lru_keys(store), ["b", "a"])
        self.assertEqual(store.get("a"), "first")
        self.assertEqual(_lru_keys(store), ["a", "b"])

    def test_delete_removes_key_from_map_and_lru(self):
        store = MiniRedis()
        store.set("a", "first")
        store.set("b", "second")
        store.set("c", "third")
        self.assertEqual(store.dbsize(), 3)

        self.assertEqual(store.delete("b"), 1)
        self.assertEqual(store.delete("b"), 0)
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.dbsize(), 2)
        self.assertEqual(store.dbsize(), store._lru.size())
        self.assertEqual(_lru_keys(store), ["c", "a"])

    def test_keys_on_empty_store(self):
        store = MiniRedis()

        self.assertEqual(store.keys(), [])
        self.assertEqual(store.dbsize(), 0)

    def test_key_queries_do_not_change_lru_order(self):
        store = MiniRedis()
        store.set("a", "first")
        store.set("b", "second")

        self.assertEqual(store.exists("a"), 1)
        self.assertEqual(_lru_keys(store), ["b", "a"])
        self.assertEqual(store.exists("missing"), 0)
        self.assertEqual(sorted(store.keys()), ["a", "b"])
        self.assertEqual(store.dbsize(), 2)
        self.assertEqual(_lru_keys(store), ["b", "a"])

    def test_info_memory_counts_utf8_bytes(self):
        store = MiniRedis()
        self.assertEqual(store.info_memory(), (0, 0, 0))

        store.set("k", "한")
        self.assertEqual(store.info_memory(), (4, 0, 0))
        store.set("키", "")
        self.assertEqual(store.info_memory(), (7, 0, 0))

    def test_overwrite_updates_memory_by_size_difference(self):
        store = MiniRedis()
        store.set("a", "old")
        store.set("b", "hi")
        self.assertEqual(store.info_memory(), (7, 0, 0))

        store.set("a", "longer")
        self.assertEqual(store.info_memory(), (10, 0, 0))
        store.set("a", "x")
        self.assertEqual(store.info_memory(), (5, 0, 0))

    def test_delete_releases_memory_only_for_existing_key(self):
        store = MiniRedis()
        store.set("a", "hi")
        store.set("키", "한")

        self.assertEqual(store.delete("키"), 1)
        self.assertEqual(store.info_memory(), (3, 0, 0))
        self.assertEqual(store.delete("키"), 0)
        self.assertEqual(store.info_memory(), (3, 0, 0))
        self.assertEqual(store.delete("a"), 1)
        self.assertEqual(store.info_memory(), (0, 0, 0))
