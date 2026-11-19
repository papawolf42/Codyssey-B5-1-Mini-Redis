# 0015 · _link_after만들었잖아 그냥 이름을 append라 짓는게 안낫나?

## Q. _link_after만들었잖아 그냥 이름을 append라 짓는게 안낫나?

---

`_link_after`는 **`append`라고 부르면 동작이 헷갈리고, 특히 나중에 `move_to_front`와도 잘 안 어울립니다.** 이유는 크게 세 가지입니다.

---

### 1. `append`는 "항상 맨 뒤에 붙인다"는 뜻이기 때문
* 파이썬 `list.append(x)`처럼 `append`는 보통 **"리스트의 제일 끝(tail)에 추가"**를 의미합니다. (`insert_back`과 같은 뜻)
* 그런데 `_link_after(prev_node, node)`는 맨 뒤에 붙이는 게 아니라 **"내가 지정한 아무 노드(`prev_node`) 바로 뒤에 끼워 넣는"** 메서드입니다.
  * `insert_front`: `self._head` 바로 뒤에 끼움
  * `insert_back`: `self._tail.prev` 바로 뒤에 끼움
* 즉 "맨 뒤에 붙인다(`append`)"가 아니라 **"특정 노드 뒤에 연결한다(`link_after`)"**가 정확한 표현입니다.

---

### 2. "새 데이터 추가"가 아니라 "노드 포인터 연결(`link`)"이기 때문
* `insert_front(data)` / `insert_back(data)`는 **`data`를 받아 새 `Node`를 만듭니다.**
* 반면 `_link_after(prev_node, node)`는 **`Node` 객체끼리 포인터만 이어주는 저수준 도우미**입니다.
* 나중에 구현할 `move_to_front(node)`에서는 **새 `Node`를 만들지 않고 기존 노드를 떼었다가(`_unlink`) 맨 앞에 다시 이어(`_link_after`) 붙입니다.**
  ```python
  self._unlink(node)              # 떼고
  self._link_after(self._head, node)  # head 뒤에 다시 붙이고
  ```
  이렇게 **`_unlink` ↔ `_link_after`**로 짝을 맞춰 두면 코드만 읽어도 *"아, 노드를 끊고 다시 잇는구나"*가 한눈에 보입니다.

---

### 3. (참고) 혹시 `insert_back` 이름을 `append`로 바꾸는 걸 뜻하셨다면
* 의미만 놓고 보면 `insert_back`은 `append`와 거의 같지만, [instruction.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/instruction.md#L87) 요구사항과 [0004-b5-1-daily-plan.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/docs/0004-b5-1-daily-plan.md#L66) 인터페이스에서 **`insert_front` / `insert_back`**으로 메서드 이름을 정해 두었기 때문에 그대로 유지하는 게 좋습니다.

---

만약 `_link_after` 대신 직관적인 이름을 고른다면 `_insert_after` 정도가 후보인데, `_unlink`와 대칭을 이루는 **`_link_after`**가 지금 구조에 가장 잘 맞습니다. 이대로 `1-b` 커밋(`feat: 이중 연결 리스트 앞뒤 삽입 구현`) 진행할까요?
