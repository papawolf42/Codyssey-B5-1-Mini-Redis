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
        self.assertEqual(_forward_data(lst), [])
        self.assertEqual(_backward_data(lst), [])


if __name__ == "__main__":
    unittest.main()
