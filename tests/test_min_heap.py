"""최소 힙의 삽입과 조회를 검증한다."""

import unittest

from mini_redis.min_heap import MinHeap


class TestMinHeap(unittest.TestCase):
    def test_empty_heap(self):
        heap = MinHeap()
        self.assertEqual(heap.size(), 0)
        self.assertIsNone(heap.peek())

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
