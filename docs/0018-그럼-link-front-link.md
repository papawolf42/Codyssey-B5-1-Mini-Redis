# 0018 · 그럼 link_front link_back 이렇게 만들지 않는이유는 뭐야?

## Q. 그럼 link_front link_back 이렇게 만들지 않는이유는 뭐야?

---

**`_link_front`와 `_link_back`을 따로 만들면, 그 두 함수 내부에서 "포인터 4개를 바꾸는 코드"가 똑같이 중복되기 때문입니다.**

---

### 1. 두 연산은 본질적으로 똑같은 일입니다
리스트에 새 노드 `node`를 끼워 넣는 상황을 보면:

* **맨 앞 연결(`_link_front`)**: **`_head`** 와 `_head.next` **사이**(`_head` 바로 뒤)에 끼우기
* **맨 뒤 연결(`_link_back`)**: **`_tail.prev`** 와 `_tail` **사이**(`_tail.prev` 바로 뒤)에 끼우기

만약 `_link_front(node)`와 `_link_back(node)`를 둘 다 만들면:
* `_link_front`: 포인터 4줄 + `self._size += 1`
* `_link_back`: 포인터 4줄 + `self._size += 1`

결국 **"어떤 기준 노드(`prev_node`) 바로 뒤에 `node`를 연결한다"**는 똑같은 동작을 함수 두 개에 중복해서 쓰게 됩니다.

---

### 2. 기준 노드만 인자로 받으면 함수 1개로 끝납니다
차이가 나는 건 오직 **"어느 노드 뒤에 붙일 것인가"** 하나뿐입니다.
* 앞쪽 기준: `self._head`
* 뒤쪽 기준: `self._tail.prev`

그래서 기준 노드를 파라미터(`prev_node`)로 빼면, **`_link_after(prev_node, node)` 함수 단 1개**로:
1. `insert_front` → `self._link_after(self._head, node)`
2. `insert_back` → `self._link_after(self._tail.prev, node)`
3. `move_to_front` → `self._link_after(self._head, node)`

**포인터 4개 조작 로직을 코드 전체에서 딱 한 곳에만 두고** 세 군데에서 모두 재사용할 수 있습니다.

---

### 3. 더미 노드 덕분에 가능한 깔끔함
만약 더미 `_head`/`_tail`이 없었다면 맨 앞 삽입 때는 `_head`가 `None`인지 검사해야 해서 `_link_after` 하나로 합치기 어렵습니다. **양 끝에 더미 노드가 항상 있기 때문에** 앞도 뒤도 모두 *"이미 존재하는 노드 바로 뒤에 붙이기"*로 통일되는 것입니다.

이해되셨으면 `1-b` 커밋(`feat: 이중 연결 리스트 앞뒤 삽입 구현`) 진행할까요?
