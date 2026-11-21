"""최소 힙의 삽입, 조회, 제거를 검증한다."""

import unittest

from mini_redis.min_heap import MinHeap


class TestMinHeap(unittest.TestCase):
    def test_empty_heap(self):
        heap = MinHeap()
        self.assertEqual(heap.size(), 0)
        self.assertIsNone(heap.peek())
        self.assertIsNone(heap.pop())

    def test_push_keeps_minimum_at_root(self):
        heap = MinHeap()
        for item in ((4, "d"), (2, "b"), (3, "c"), (5, "e")):
            heap.push(item)
        self.assertEqual(heap.peek(), (2, "b"))

        heap.push((1, "a"))
        self.assertEqual(heap.peek(), (1, "a"))
        self.assertEqual(heap.size(), 5)

    def test_peek_leaves_item_in_heap(self):
        heap = MinHeap()
        heap.push((1, "a"))

        self.assertEqual(heap.peek(), (1, "a"))
        self.assertEqual(heap.peek(), (1, "a"))
        self.assertEqual(heap.size(), 1)

    def test_pop_only_item(self):
        heap = MinHeap()
        heap.push((1, "a"))

        self.assertEqual(heap.pop(), (1, "a"))
        self.assertEqual(heap.size(), 0)
        self.assertIsNone(heap.peek())

    def test_pop_returns_items_in_order(self):
        heap = MinHeap()
        items = (
            (1, "a"), (3, "c"), (2, "b"), (4, "d"),
            (5, "e"), (6, "f"), (9, "i"),
        )
        for item in items:
            heap.push(item)

        self.assertEqual(heap.pop(), (1, "a"))
        self.assertEqual(heap.peek(), (2, "b"))
        self.assertEqual(heap.size(), 6)
        self.assertEqual([heap.pop() for _ in range(6)], sorted(items)[1:])
        self.assertIsNone(heap.pop())

    def test_pop_breaks_equal_expiration_times_by_key(self):
        heap = MinHeap()
        for key in ("c", "a", "b"):
            heap.push((5, key))

        self.assertEqual(
            [heap.pop() for _ in range(3)], [(5, "a"), (5, "b"), (5, "c")]
        )
