# 0004 · Entry 구조와 DLL, MRU, LRU 개념 정리

## Q. Entry 상자, expire_at, lru_node, DLL, MRU, LRU가 각각 무엇이고 어떻게 연결되나요?

---

### 1. 용어 한눈에 정리

- **Entry (보관 상자):**  
  키 하나에 대해 필요한 모든 정보를 한데 묶어둔 객체입니다.  
  보통 `Entry{value, expire_at, lru_node}` 형태로 구성됩니다.
  - `value`: 실제 저장된 값 (예: `"Bob"`)
  - `expire_at`: 언제 만료되는지 적어둔 미래 시각 (예: `103.0초`, 없으면 `None`)
  - `lru_node`: DLL 줄 안에서 내가 서 있는 칸의 위치 주소 (포인터)

- **DLL (Doubly Linked List · 이중 연결 리스트):**  
  각 칸(노드)이 **앞 노드(`prev`)**와 **뒷 노드(`next`)**의 손을 동시에 잡고 있는 연결 구조입니다.
  - 양손을 잡고 있기 때문에 줄 중간에 있는 노드를 쏙 빼서 맨 앞으로 옮길 때, 앞뒤 사람만 서로 손잡아 주면 되므로 **O(1)**로 이동이 끝납니다.

- **MRU (Most Recently Used):**  
  "가장 최근에 사용된 키" → DLL 줄의 **맨 앞(Front)**입니다.  
  `SET`이나 `GET`으로 방금 건드린 키는 항상 맨 앞으로 옵니다.

- **LRU (Least Recently Used):**  
  "가장 오랫동안 사용되지 않은 키" → DLL 줄의 **맨 뒤(Back)**입니다.  
  메모리 제한(`maxmemory`)을 초과하면 여기서부터 차례대로 쫓겨납니다(Eviction).

---

### 2. 전체 연결 다이어그램

```text
HashMap ("user:2")
    │
    ▼ O(1) 바로 찾기
Entry 상자
 ├── value: "Bob"
 ├── expire_at: 103초 ──────────► Min Heap 맨 꼭대기에 등록 (유통기한 감시)
 └── lru_node (줄 위치) ──────┐
                             │ O(1) 직접 점프!
                             ▼
DLL: [MRU: 맨 앞] user:3 ⇄ (user:2) ⇄ user:1 [LRU: 맨 뒤]
```

### 3. GET user:2 를 실행하면 일어나는 일

1. **HashMap**에서 `"user:2"`로 `Entry` 상자를 O(1)로 찾습니다.
2. 만약 만료 시각(`expire_at`)이 지났다면 삭제하고 `(nil)` 반환.
3. 살아있다면, `entry.lru_node`를 이용해 **DLL에서 user:2 노드를 쏙 빼서 맨 앞(MRU)으로 옮깁니다** (O(1)).
4. 결과값 `"Bob"`을 반환합니다.

> 💡 더 생생한 그림과 버튼 클릭 시뮬레이션은 같은 폴더의 [0001-mini-redis-visual-guide.html](./0001-mini-redis-visual-guide.html)을 참고하세요.
