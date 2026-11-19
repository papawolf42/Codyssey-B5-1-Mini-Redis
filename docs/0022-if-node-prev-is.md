# 0022 · if node.prev is None or node.next is None: 이런경우가 있

## Q. if node.prev is None or node.next is None: 이런경우가 있을수있나???

---

**네, 실제로 꽤 자주 생길 수 있는 상황입니다!** 크게 두 가지 경우입니다.

---

### 1. 이미 제거된 노드를 실수로 한 번 더 지우거나 옮기려 할 때 (가장 흔함)
`_unlink(node)` 코드를 보면 노드를 떼어낸 뒤 이렇게 정리합니다:
```python
node.prev = None
node.next = None
```
만약 어떤 노드에 대해 `remove_node(node)`나 `remove_front()`/`remove_back()`이 이미 한 번 실행된 뒤, 실수로 같은 `node`를 넘겨서 `remove_node(node)`나 `move_to_front(node)`를 **두 번째로 호출**하면 `node.prev`와 `node.next`가 **`None`**인 상태입니다.

* **이 방어 조건이 없을 때:** `_unlink` 안의 `node.prev.next`에서 **`AttributeError: 'NoneType' object has no attribute 'next'`** 에러로 프로그램이 즉시 터집니다.
* **이 방어 조건이 있을 때:** 크래시 없이 조용히 빠져나가고, `_size`도 잘못 깎이지 않습니다.

*(참고로 나중에 `MiniRedis` 구현할 때 `remove_back()`으로 노드를 뺀 뒤 또 `remove_node()`를 부르거나, 삭제 경로가 두 번 타는 버그가 흔한 함정입니다.)*

---

### 2. 리스트에 넣지 않은 새 `Node`를 바로 넘겼을 때
누군가 `n = Node("A")`만 직접 만들고 리스트에 `insert_*` 하지 않은 채로 `lst.remove_node(n)`이나 `lst.move_to_front(n)`을 호출하면, `n.prev`와 `n.next`가 초기값 `None`이므로 역시 `AttributeError`를 막아줍니다.

---

### (보너스) 사실 더미 노드도 이 조건에 걸립니다
더미 `_head`는 `prev is None`, 더미 `_tail`은 `next is None`입니다. 다만 윗줄에 `node is None or node is self._head or node is self._tail`을 따로 적어두면 *"아, 더미 노드는 절대 지우지 않는구나"*가 코드만 읽어도 바로 드러나서 같이 두는 편이 읽기 좋습니다.

*(반대로 **다른 리스트 객체(`lst2`)**에 연결된 노드를 `lst1.remove_node(...)`에 넘기는 경우까진 이 조건만으로 못 막지만, 최소한 **이미 떼어진 노드 재사용 실수**는 완벽하게 막아줍니다.)*

---

이해되셨다면 `1-d` 커밋 진행할까요? (아까 제안드린 1~3번 중 번호를 골라주세요!)
1. **`feat: 지정 노드 제거·맨 앞 이동 구현`**
2. **`feat: 노드 참조 기반 삭제·LRU 이동 구현`**
3. **`feat: remove_node, move_to_front 구현`**
