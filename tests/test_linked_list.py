"""DoublyLinkedList 단위 테스트."""

import unittest

from mini_redis.linked_list import DoublyLinkedList


def _forward_data(lst):
    """앞에서 뒤로 순회한 노드 data 목록을 반환한다."""
    return [n.data for n in lst]


def _backward_data(lst):
    """뒤에서 앞으로 prev 포인터를 따라간 노드 data 목록을 반환한다."""
    result = []
    cur = lst._tail.prev
    while cur is not lst._head:
        result.append(cur.data)
        cur = cur.prev
    return result


class TestDoublyLinkedList(unittest.TestCase):
    """이중 연결 리스트의 기본 구조와 순회 동작을 검증한다."""

    def test_empty_list(self):
        lst = DoublyLinkedList()
        self.assertEqual(lst.size(), 0)
        self.assertIsNone(lst.remove_front())
        self.assertIsNone(lst.remove_back())
        self.assertEqual(_forward_data(lst), [])
        self.assertEqual(_backward_data(lst), [])

    def test_insert_front_order_and_returns_node(self):
        lst = DoublyLinkedList()
        n1 = lst.insert_front("A")
        n2 = lst.insert_front("B")
        n3 = lst.insert_front("C")

        self.assertEqual(n1.data, "A")
        self.assertEqual(n2.data, "B")
        self.assertEqual(n3.data, "C")
        self.assertEqual(lst.size(), 3)
        self.assertEqual(_forward_data(lst), ["C", "B", "A"])
        self.assertEqual(_backward_data(lst), ["A", "B", "C"])

    def test_insert_back_order(self):
        lst = DoublyLinkedList()
        lst.insert_back("A")
        lst.insert_back("B")
        lst.insert_back("C")

        self.assertEqual(lst.size(), 3)
        self.assertEqual(_forward_data(lst), ["A", "B", "C"])
        self.assertEqual(_backward_data(lst), ["C", "B", "A"])

    def test_remove_front_and_back(self):
        lst = DoublyLinkedList()
        lst.insert_back("A")
        lst.insert_back("B")
        lst.insert_back("C")

        front = lst.remove_front()
        self.assertEqual(front.data, "A")
        self.assertIsNone(front.prev)
        self.assertIsNone(front.next)
        self.assertEqual(lst.size(), 2)
        self.assertEqual(_forward_data(lst), ["B", "C"])

        back = lst.remove_back()
        self.assertEqual(back.data, "C")
        self.assertIsNone(back.prev)
        self.assertIsNone(back.next)
        self.assertEqual(lst.size(), 1)
        self.assertEqual(_forward_data(lst), ["B"])
        self.assertEqual(_backward_data(lst), ["B"])


if __name__ == "__main__":
    unittest.main()
