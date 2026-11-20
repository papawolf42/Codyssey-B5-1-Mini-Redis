# 0041 · 그럼 그냥 항상 capacity로 나누고, 단일진실공급하면되나?

## Q. 그럼 그냥 항상 capacity로 나누고, 단일진실공급하면되나?

---

**네, 정확합니다!** 특히 **`@property`로 `len(self._buckets)` 하나만 바라보게 하면 완벽한 단일 진실(Single Source of Truth)**이 됩니다.

---

### 두 가지 방법 비교

1. **가장 깔끔한 단일 진실 (`@property` 방식 — 추천)**
   ```python
   def __init__(self, capacity=8):
       ...
       self._buckets = [DoublyLinkedList() for _ in range(capacity)]
       self._size = 0

   @property
   def capacity(self):
       """현재 버킷 배열의 크기를 반환한다."""
       return len(self._buckets)

   def _index(self, key):
       return fnv1a_32(key) % self.capacity
   ```
   * **장점:** 실제 버킷 배열(`self._buckets`) 길이 하나만 진짜 기준이고, `hm.capacity`도 `len(self._buckets)`(O(1))를 그대로 읽습니다.
   * 다음 `3-a` 확장(`_resize`) 때도 **`self._buckets = new_buckets` 하나만 바꾸면 `capacity`와 `_index` 나눗셈이 자동으로 함께 바뀌어서 절대 어긋날 수 없습니다.**

2. **단순 속성 유지 방식**
   * `__init__`에 `self.capacity = capacity`를 그대로 두고 `_index`만 `fnv1a_32(key) % self.capacity`로 맞추는 방식입니다.
   * 다만 `_resize`할 때 `self._buckets`와 `self.capacity` 두 군데를 꼭 같이 갱신해야 합니다.

---

**1번(`@property` + `_index`에서 `self.capacity` 사용)**으로 바로 고쳐서 테스트 돌린 뒤 `2-b` 커밋(`feat: 체이닝 해시맵 기본 연산(put/get/contains/keys/size)`)까지 진행할까요, 아니면 수정한 뒤 먼저 보여드릴까요?
