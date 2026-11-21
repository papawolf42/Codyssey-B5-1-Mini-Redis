"""Mini Redis의 문자열 저장과 최근 사용 순서를 검증한다."""

import unittest

from mini_redis.store import MiniRedis, OOMError


def _lru_keys(store):
    return [node.data for node in store._lru]


class FakeClock:
    """테스트에서 필요할 때만 시간이 흐르는 시계."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


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

    def test_set_evicts_oldest_key_when_memory_limit_is_exceeded(self):
        store = MiniRedis()
        store.config_set_maxmemory(30)
        store.set("user:1", "Alice")
        store.set("user:2", "Bob")
        store.set("user:3", "Charlie")

        self.assertIsNone(store.get("user:1"))
        self.assertEqual(sorted(store.keys()), ["user:2", "user:3"])
        self.assertEqual(store.info_memory(), (22, 30, 1))

    def test_overwrite_moves_key_to_front_before_evicting(self):
        store = MiniRedis()
        store.config_set_maxmemory(8)
        store.set("a", "old")
        store.set("b", "two")
        self.assertEqual(store.info_memory(), (8, 8, 0))

        store.set("a", "newer")

        self.assertEqual(store.get("a"), "newer")
        self.assertIsNone(store.get("b"))
        self.assertEqual(store.info_memory(), (6, 8, 1))

    def test_zero_memory_limit_is_unlimited(self):
        store = MiniRedis()
        store.config_set_maxmemory(4)
        store.set("a", "one")
        store.config_set_maxmemory(0)
        store.set("b", "second")

        self.assertEqual(sorted(store.keys()), ["a", "b"])
        self.assertEqual(store.info_memory(), (11, 0, 0))

    def test_set_can_evict_multiple_keys_and_counts_accumulate(self):
        store = MiniRedis()
        store.config_set_maxmemory(10)
        for key in ("a", "b", "c"):
            store.set(key, "hi")

        store.set("d", "1234567")
        self.assertEqual(store.keys(), ["d"])
        self.assertEqual(store.info_memory(), (8, 10, 3))

        store.set("e", "hi")
        self.assertEqual(store.keys(), ["e"])
        self.assertEqual(store.info_memory(), (3, 10, 4))

    def test_oversized_set_leaves_store_unchanged(self):
        store = MiniRedis()
        store.config_set_maxmemory(10)
        store.set("k", "old")
        store.set("a", "other")

        for key in ("k", "b"):
            with self.subTest(key=key):
                with self.assertRaises(OOMError):
                    store.set(key, "1234567890")
                self.assertEqual(_lru_keys(store), ["a", "k"])
                self.assertEqual(store.info_memory(), (10, 10, 0))
                self.assertEqual(sorted(store.keys()), ["a", "k"])

        self.assertEqual(store.get("k"), "old")
        self.assertEqual(store.get("a"), "other")

    def test_lowering_memory_limit_evicts_immediately(self):
        store = MiniRedis()
        store.config_set_maxmemory(12)
        for key in ("a", "b", "c"):
            store.set(key, "hi")
        store.get("a")

        store.config_set_maxmemory(6)

        self.assertEqual(store.info_memory(), (6, 6, 1))
        self.assertEqual(sorted(store.keys()), ["a", "c"])
        self.assertEqual(_lru_keys(store), ["a", "c"])

    def test_ttl_reports_missing_no_expiry_and_remaining_seconds(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        self.assertEqual(store.ttl("a"), -2)

        store.set("a", "hello")
        self.assertEqual(store.ttl("a"), -1)
        self.assertEqual(store.expire("a", 3), 1)
        self.assertEqual(store.ttl("a"), 3)
        clock.advance(0.001)
        self.assertEqual(store.ttl("a"), 2)
        clock.advance(2.5)
        self.assertEqual(store.ttl("a"), 0)
        clock.advance(0.5)
        self.assertEqual(store.ttl("a"), -2)

    def test_expire_replaces_previous_deadline(self):
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        store.set("a", "hello")
        store.expire("a", 3)
        store.expire("a", 10)

        clock.advance(5)
        self.assertEqual(store.get("a"), "hello")
        self.assertEqual(store.ttl("a"), 5)

    def test_expire_missing_key_returns_zero(self):
        store = MiniRedis()
        self.assertEqual(store.expire("missing", 3), 0)

    def test_nonpositive_expiry_deletes_key_immediately(self):
        store = MiniRedis()
        for seconds in (0, -5):
            with self.subTest(seconds=seconds):
                store.set("a", "hello")
                self.assertEqual(store.expire("a", seconds), 1)
                self.assertIsNone(store.get("a"))
                self.assertEqual(store.ttl("a"), -2)

    def test_set_overwrite_clears_expiry(self):
        store = MiniRedis(clock=FakeClock())
        store.set("a", "old")
        store.expire("a", 3)

        store.set("a", "new")

        self.assertEqual(store.ttl("a"), -1)
