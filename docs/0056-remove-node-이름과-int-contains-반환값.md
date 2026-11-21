# 0056 · `remove_node` 이름 유지 이유와 `int(self._map.contains(key))`

## Q. ① `remove_node`를 그냥 `remove`로 바꾸면 안 되나요? ② `int(self._map.contains(key))`는 노드를 `int`로 바꾸는 건가요?

---

### 1. 왜 `remove` 대신 `remove_node`라는 이름을 유지할까요?

1. **과제 명세(`instruction.md` 4-1장)의 지정 이름:**  
   스펙에 이중 연결 리스트의 주요 메서드로 `remove_node`가 그대로 적혀 있습니다.
2. **오해를 막는 명확한 뜻:**  
   보통 `remove("a")`라고 하면 *"값 `"a"`를 찾아서 지워줘"*처럼 들리지만,  
   `remove_node(node)`라고 쓰면 **"값으로 찾지 않고, 노드 객체(주소) 자체를 받아서 0.0001초(O(1))에 떼어 낸다"**는 의도가 이름만 봐도 딱 드러납니다.

---

### 2. `int(self._map.contains(key))`는 노드를 숫자로 바꾸는 걸까요?

**아닙니다! 노드가 아니라 `True` / `False`(참·거짓)를 숫자 `1` / `0`으로 바꾸는 거예요!**

안쪽을 뜯어보면 2단계로 나뉩니다:
```python
# 1단계: HashMap.contains(key) 안쪽
return self._find_node(bucket, key) is not None   # 결과가 True 또는 False!

# 2단계: Store.exists(key)
return int(self._map.contains(key))               # int(True) -> 1, int(False) -> 0
```

- `_find_node()`가 노드를 찾아온 뒤, `is not None` 비교를 거쳐 **`contains()`는 오직 `True` 또는 `False`만 반환**합니다.
- 파이썬에서는 `int(True) == 1`, `int(False) == 0`이므로, `EXISTS` 명령어의 결과(`1` 또는 `0`)를 한 줄로 깔끔하게 돌려주기 위해 `int(...)`를 쓴 것입니다.
