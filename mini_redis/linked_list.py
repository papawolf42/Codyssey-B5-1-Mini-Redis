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
