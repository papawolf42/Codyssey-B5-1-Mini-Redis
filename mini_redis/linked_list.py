"""이중 연결 리스트(Doubly Linked List) 모듈."""


class Node:
    """이중 연결 리스트의 노드.

    prev와 next 포인터를 모두 들고 있어, 노드 참조만 알면
    앞뒤 노드를 훑지 않고도 O(1)에 연결을 끊거나 옮길 수 있다.
    """

    def __init__(self, data):
        """노드를 생성한다. 인자: data(저장할 값)."""
        self.prev = None
        self.next = None
        self.data = data


class DoublyLinkedList:
    """더미 head/tail 노드를 사용하는 이중 연결 리스트.

    양 끝에 센티널(더미) 노드를 두어 빈 리스트나 양 끝단 처리 시
    별도 None 분기 없이 동일한 포인터 조작으로 O(1) 연산을 보장한다.
    """

    def __init__(self):
        """빈 이중 연결 리스트를 초기화한다."""
        self._head = Node(None)
        self._tail = Node(None)
        self._head.next = self._tail
        self._tail.prev = self._head
        self._size = 0

    def _link_front(self, node):
        """더미 head 바로 뒤에 node를 연결한다. 포인터 4개만 바꿔 O(1)."""
        next_node = self._head.next
        node.prev = self._head
        node.next = next_node
        self._head.next = node
        next_node.prev = node
        self._size += 1

    def _link_back(self, node):
        """더미 tail 바로 앞에 node를 연결한다. 포인터 4개만 바꿔 O(1)."""
        prev_node = self._tail.prev
        node.prev = prev_node
        node.next = self._tail
        prev_node.next = node
        self._tail.prev = node
        self._size += 1

    def _unlink(self, node):
        """리스트에서 node를 떼어낸다. 양옆 포인터 2개만 바꿔 O(1)."""
        node.prev.next = node.next
        node.next.prev = node.prev
        node.prev = None
        node.next = None
        self._size -= 1

    def insert_front(self, data):
        """맨 앞에 data를 담은 노드를 추가하고 해당 Node를 반환한다. (O(1))"""
        node = Node(data)
        self._link_front(node)
        return node

    def insert_back(self, data):
        """맨 뒤에 data를 담은 노드를 추가하고 해당 Node를 반환한다. (O(1))"""
        node = Node(data)
        self._link_back(node)
        return node

    def remove_front(self):
        """맨 앞 노드를 제거해 반환한다. 비어 있으면 None을 반환한다. (O(1))"""
        if self._size == 0:
            return None
        node = self._head.next
        self._unlink(node)
        return node

    def remove_back(self):
        """맨 뒤 노드를 제거해 반환한다. 비어 있으면 None을 반환한다. (O(1))"""
        if self._size == 0:
            return None
        node = self._tail.prev
        self._unlink(node)
        return node

    def peek_back(self):
        """맨 뒤 노드를 반환한다. 비어 있으면 None을 반환한다. (O(1))"""
        if self._size == 0:
            return None
        return self._tail.prev

    def _is_linked_node(self, node):
        """더미가 아니고 현재 리스트에 연결된 노드인지 확인한다."""
        if node is None or node is self._head or node is self._tail:
            return False
        return node.prev is not None and node.next is not None

    def remove_node(self, node):
        """주어진 노드를 즉시 제거한다. prev/next를 직접 알고 있어 O(1)."""
        if not self._is_linked_node(node):
            return None
        self._unlink(node)
        return node

    def move_to_front(self, node):
        """주어진 노드를 맨 앞으로 옮긴다. unlink 후 head 뒤 연결로 O(1)."""
        if not self._is_linked_node(node) or self._head.next is node:
            return
        self._unlink(node)
        self._link_front(node)

    def size(self):
        """현재 저장된 노드 개수를 정수로 반환한다. (O(1))"""
        return self._size

    def __iter__(self):
        """앞에서부터 뒤로 Node 객체를 순서대로 순회한다."""
        cur = self._head.next
        while cur is not self._tail:
            nxt = cur.next
            yield cur
            cur = nxt
