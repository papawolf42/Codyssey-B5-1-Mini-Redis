# 0039 · 왜 기본 capacity를 8로 둔 근거가 뭐야? 아 그럼 8개의 버킬(DLL)이 생긴건가

## Q. 왜 기본 capacity를 8로 둔 근거가 뭐야? 아 그럼 8개의 버킬(DLL)이 생긴건가? 이번 커밀 총 줄수가 몇줄이야?         for node in bucket: 이걸로 DLL을 순회할 수 있나?     def __iter__(self): 가 있어서 가능한건가?             if node.data[0] == key: 이건 왜 [0]으로 접근하지? node는 하나의 연결리스트 요소일건데, 여기 data가 배열로되어있나? DLL도 자체 size가 있는데 Hashmap도 자체 size를 관리하네? 이는 이중으로 관리하는 셈 아닌가?         return node.data[1] 이건 왜 배열 1번을 리턴해?

---

궁금하신 6가지를 하나씩 정리해 드립니다.

---

### 1. 왜 기본 `capacity`가 `8`인가요? 정말 DLL이 8개 생기나요?
* **네, 실제로 8개의 빈 `DoublyLinkedList`가 생깁니다.**
  `[DoublyLinkedList() for _ in range(8)]` 덕분에 빈 칸 8개 각각에 연결 리스트 인스턴스가 1개씩 들어갑니다.
* **왜 하필 `8`인가?**
  1. **2배 확장에 깔끔한 2의 거듭제곱** (`8 → 16 → 32 → 64 ...`). 파이썬 내장 `dict`의 초기 크기도 `8`입니다.
  2. **적당한 균형점:** 너무 작으면(`2`나 `4`) 몇 개만 넣어도 바로 확장이 일어나고, 너무 크면(`64` 이상) 키 몇 개 안 쓰는데 빈 `DoublyLinkedList` 객체(각각 더미 노드 2개 포함)를 많이 만들어 메모리를 낭비합니다. `8`은 가볍게 시작하면서 7개째에 첫 확장이 일어나 학습·테스트하기에도 적당한 크기입니다. ([0004-b5-1-daily-plan.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/docs/0004-b5-1-daily-plan.md#L74) 인터페이스 기준값)

---

### 2. 이번 커밋 총 줄 수는 몇 줄인가요?
`git diff --stat` 기준 **총 116줄 추가, 1줄 삭제**입니다:
* [hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/hash_map.py): **`+64`줄**
* [test_hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/tests/test_hash_map.py): **`+53`줄, `-1`줄**

---

### 3. `for node in bucket:`이 가능한 이유 → `__iter__` 덕분인가요?
**네, 정확합니다!**
* 파이썬은 `for node in bucket:`을 실행할 때 자동으로 `bucket.__iter__()`를 호출합니다.
* 1일차에 [linked_list.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/linked_list.py)에 `def __iter__(self):`를 만들고 `yield cur`로 **`Node` 객체를 앞에서부터 하나씩 내보내도록** 구현해 두었기 때문에, `bucket`을 바로 `for`문에 넣을 수 있는 것입니다.

---

### 4. `node.data[0]`, `node.data[1]`은 왜 인덱스로 접근하나요? (`data`가 배열인가요?)
배열(list)이 아니라 **`(key, value)` 2칸짜리 튜플**입니다! `put()`에서 버킷에 이렇게 저장합니다:
```python
bucket.insert_back((key, value))
```
* 같은 버킷에 해시 충돌로 여러 키(`"k0"`, `"k8"`)가 한꺼번에 들어올 수 있기 때문에, `value`만 저장하면 이게 누구의 값인지 구분할 수 없습니다.
* 그래서 `node.data`에 **`(key, value)` 쌍을 통째로** 넣어두고:
  * **`node.data[0]`** → **`key`** (내가 찾는 키가 맞는지 비교: `if node.data[0] == key:`)
  * **`node.data[1]`** → **`value`** (찾았을 때 값을 꺼내 반환: `return node.data[1]`)

---

### 5. DLL도 `size`가 있는데 `HashMap`도 `_size`를 따로 관리하면 이중 관리 아닌가요?
**맞습니다. 의도적인 "캐싱(이중 보관)"입니다.**

만약 `HashMap`이 `self._size`를 따로 들고 있지 않다면:
1. `hm.size()`를 부를 때마다 **모든 버킷(`self._buckets`)을 처음부터 끝까지 돌며** 각 버킷의 `size()`를 전부 더해야 합니다 → **O(capacity)**로 느려짐.
2. 특히 `3-a`에서 `put()`을 할 때마다 **로드 팩터(`size / capacity > 0.75`)**를 검사해야 하는데, 그때마다 버킷 전체를 다 세면 `put()`까지 느려집니다.

반면 `HashMap._size`를 하나 두면 **`hm.size()`와 로드 팩터 검사가 모두 O(1)**이 됩니다. *(참고로 `DLL._size`는 "버킷 1칸의 길이", `HashMap._size`는 "버킷 전체의 총 키 개수"로 역할 범위도 다릅니다.)*

---

설명이 되셨다면 `2-b` 커밋할까요?
1. **`feat: 체이닝 해시맵 기본 연산 구현`**
2. **`feat: 체이닝 해시맵 저장·조회 기능 구현`**
