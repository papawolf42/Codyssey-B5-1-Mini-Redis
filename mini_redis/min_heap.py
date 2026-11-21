"""최소 힙(Min Heap) 모듈."""


class MinHeap:
    """배열로 표현한 최소 힙. 가장 작은 항목을 맨 앞에 둔다."""

    def __init__(self):
        """빈 힙을 초기화한다."""
        self._items = []

    def push(self, item):
        """비교 가능한 항목을 추가한다. 부모만 따라 올라가므로 O(log n)이다."""
        self._items.append(item)
        self._heapify_up(len(self._items) - 1)

    def _heapify_up(self, index):
        """새 항목이 부모보다 작으면 자리를 바꿔 힙의 순서를 복구한다."""
        while index > 0:
            parent = (index - 1) // 2
            if self._items[parent] <= self._items[index]:
                break
            self._items[parent], self._items[index] = (
                self._items[index], self._items[parent]
            )
            index = parent

    def peek(self):
        """최솟값을 꺼내지 않고 반환한다. 비어 있으면 None을 반환한다."""
        if not self._items:
            return None
        return self._items[0]

    def size(self):
        """현재 저장된 항목 수를 반환한다."""
        return len(self._items)
