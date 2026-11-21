# 0058 · `peek_back().data`가 `None.data`로 터지지 않는 이유 (불변식)

## Q. `oldest = self._lru.peek_back(); self._remove_key(oldest.data)`에서 `peek_back()`이 `None`이면 `None.data` 에러가 나지 않나요?

---

### 1. 날카로운 의문: 만약 `oldest`가 `None`이면?

맞습니다! 만약 `_lru` 리스트가 텅 비어 있어서 `peek_back()`이 `None`을 돌려줬는데 그대로 `oldest.data`를 읽으면, 파이썬은 즉시 **`AttributeError: 'NoneType' object has no attribute 'data'`**를 내며 멈춥니다.

---

### 2. 그런데 왜 실제 코드에서는 안전할까요? (3가지 장부의 일치)

바로 위 줄의 `while` 조건을 보면 비밀이 풀립니다:

```python
while self._maxmemory > 0 and self._used_memory > self._maxmemory:
    oldest = self._lru.peek_back()
    self._remove_key(oldest.data)
    self._evicted_keys += 1
```

1. `while` 안으로 들어오려면 **`_used_memory > _maxmemory > 0`**, 즉 **`_used_memory`가 반드시 0보다 커야** 합니다.
2. 저장소가 비어 있다면 `_used_memory`는 **`0`**이므로 애초에 이 `while` 문 안으로 한 발짝도 들어올 수 없습니다.
3. `_used_memory`가 `0`보다 크다는 뜻은 **저장소에 살아 있는 키가 최소 1개 이상 반드시 들어 있다**는 뜻이므로, `peek_back()`은 절대로 `None`이 될 수 없습니다!
4. 마지막 1개까지 지우면 `_remove_key()`가 `_used_memory`를 `0`으로 내려주므로, 다음 바퀴의 `while` 조건에서 바로 멈춥니다.

> 💡 **핵심 교훈:** 이렇게 코드 전체에서 *"해시맵 개수 · `_lru` 길이 · `_used_memory` 세 장부가 항상 똑같이 함께 바뀐다"*는 약속을 **불변식(Invariant)**이라고 합니다. 모든 추가/삭제 경로가 한곳으로 통일되어 있기에 가능한 안전성입니다.
