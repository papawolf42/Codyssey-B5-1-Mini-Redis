# 0025 · if node is None or node is self._head or node is s

## Q. if node is None or node is self._head or node is self._tail:
            return None
        if node.prev is None or node.next is None:
            return None 이게 반복되는데 이건 함수로 빼긴 힘든가?

---

**전혀 힘들지 않고, 오히려 함수로 빼면 훨씬 깔끔해집니다!**

반환값은 달라도(`remove_node`는 `return None`, `move_to_front`는 `return`), 검사하는 조건 자체는 **"이 노드가 리스트에 실제로 연결된 유효한 노드인가?"**라는 **`True`/`False` 판정**으로 완전히 같기 때문입니다.

---

### 이렇게 뺄 수 있습니다
```python
    def _is_linked_node(self, node):
        """더미가 아니고 현재 리스트에 연결된 노드인지 확인한다."""
        if node is None or node is self._head or node is self._tail:
            return False
        return node.prev is not None and node.next is not None
```

그러면 두 메서드가 이렇게 줄어듭니다:
```python
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
```

* 4줄짜리 중복 조건문이 사라지고,
* `_is_linked_node(node)`라는 이름 덕분에 *"리스트에 붙어 있는 노드가 아니면 건너뛴다"*는 의도도 더 잘 읽힙니다.

지금 [linked_list.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/linked_list.py)에 바로 적용하고 테스트 다시 돌린 뒤 커밋 전 상태로 보여드릴까요?
