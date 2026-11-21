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

    def pop(self):
        """최솟값을 꺼내 반환한다. 비어 있으면 None을 반환한다."""
        if not self._items:
            return None

        minimum = self._items[0]
        last = self._items.pop()
        if self._items:
            self._items[0] = last
            self._heapify_down(0)
        return minimum

    def _heapify_down(self, index):
        """더 작은 자식과 바꾸며 한 경로만 내려가 힙의 순서를 복구한다."""
        size = len(self._items)
        while True:
            left = 2 * index + 1
            if left >= size:
                return

            right = left + 1
            smaller_child = left
            if right < size and self._items[right] < self._items[left]:
                smaller_child = right

            if self._items[index] <= self._items[smaller_child]:
                return
            self._items[index], self._items[smaller_child] = (
                self._items[smaller_child], self._items[index]
            )
            index = smaller_child

    def peek(self):
        """최솟값을 꺼내지 않고 반환한다. 비어 있으면 None을 반환한다."""
        if not self._items:
            return None
        return self._items[0]

    def size(self):
        """현재 저장된 항목 수를 반환한다."""
        return len(self._items)
