# 0054 · DLL을 `_lru`라 부르는 이유와 `lru_node` 객체 참조

## Q. DLL을 왜 `_lru`라고 부르며, `Entry(value, lru_node)`가 `lru_node`를 들고 있는 건 포인터를 들고 있는 것과 비슷한가요?

---

### 1. `DLL` vs `_lru` — “부품 이름”과 “역할 이름”의 차이

비유하자면 **“바퀴(DLL)”**와 **“앞바퀴(`_lru`)”** 같은 차이입니다.
- **`DoublyLinkedList (DLL)`:** 자료구조(부품) 자체의 이름입니다. 해시맵 버킷 안에서도 쓰고, 최근 사용 순서 줄에서도 씁니다.
- **`self._lru`:** `MiniRedis` 저장소 안에서 그 리스트가 맡은 **역할 이름**입니다!  
  (`LRU` = *Least Recently Used*, 즉 **"가장 오래 안 쓴 키를 골라내는 담당 줄"**이라는 뜻)

---

### 2. `lru_node`를 들고 있는 건 포인터와 같나요?

**네! 정확히 맞습니다. 파이썬에서는 이를 “객체 참조(Object Reference, 주소 쪽지)”라고 부릅니다.**

```text
해시맵 (HashMap)
  "a"  ───►  Entry(value="hello")
                │
                └── lru_node (주소 쪽지) ───┐
                                           ▼
최근 사용 줄 (self._lru)   head ⇄ ["b"] ⇄ ["a"] ⇄ tail
```

1. 처음 `SET a hello`를 할 때 `self._lru.insert_front("a")`는 줄 맨 앞에 새 노드를 만들고, **그 노드 자체를 돌려줍니다.**
2. `Entry` 상자 안의 `lru_node` 칸에 **바로 그 노드 주소 쪽지**를 꽂아 둡니다.
3. 나중에 `GET a`를 하면 해시맵에서 `Entry`를 0.0001초(O(1))에 찾고, `entry.lru_node` 쪽지를 보고 **리스트를 처음부터 뒤지지 않고 바로 `["a"]` 노드로 점프**해서 맨 앞으로 옮깁니다(`move_to_front`, O(1))!

> 💡 **`lru_node`라는 주소 쪽지가 없다면?** `GET a`를 할 때마다 `_lru` 줄을 처음부터 끝까지 걸어가며 `"a"`를 찾아야 해서 **O(N)**으로 느려졌을 겁니다.
