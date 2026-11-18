# 0014 · 왜 itr에는 next를 다 안쓰고 nxt를 쓰는거야. 실제로 _가 그런 강제력이있는거야?

## Q. 왜 itr에는 next를 다 안쓰고 nxt를 쓰는거야. 실제로 _가 그런 강제력이있는거야? 아니면 그런 약속을 사람들끼리 하고 휴먼 룰을 정한거야? 실제로 public private으로 지정되는거야 문법적으로?

---

### 1. 왜 `__iter__`에서는 `next` 대신 `nxt`를 썼을까?
두 가지 이유가 있습니다.

1. **파이썬 내장 함수 `next()`와 이름이 겹치기 때문 (가장 큰 이유)**
   * 파이썬에는 이미 **`next()`라는 내장 함수**가 있습니다.
   * 지역 변수로 `next = curr.next`라고 써도 실행은 되지만, 그 함수 안에서 내장 함수 `next()`를 가려버려(shadowing) 린터/IDE에서 경고가 뜹니다. 그래서 보통 `nxt`나 `next_node`로 피해 씁니다.
   * *(참고: `curr.next`는 `Node` 객체 안의 속성이라 내장 함수 이름 공간과 안 겹쳐서 `next`를 그대로 씁니다.)*

2. **왜 굳이 `yield curr` 전에 `nxt`를 미리 변수에 담아둘까?**
   * 만약 `for node in lst:`로 순회하는 도중에 바깥에서 `lst.remove_node(node)`로 현재 노드를 삭제해 버리면, `curr.next`가 `None`으로 바뀌어 다음 루프가 끊깁니다.
   * `yield` 전에 **`nxt = curr.next`를 미리 챙겨두면**, 순회 중 현재 노드가 제거되더라도 다음 노드로 안전하게 넘어갈 수 있습니다.

---

### 2. `_`(언더바)는 문법적 강제력이 있나, 휴먼 룰인가?
**문법적 강제력이 없는 순수한 휴먼 룰(약속)입니다.**

* 파이썬에는 Java/C++의 `public`, `private`, `protected` 키워드가 없고, 실제로도 `lst._head`나 `lst._size`를 밖에서 읽거나 고쳐도 파이썬은 막지 않습니다. (실제로 [test_linked_list.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/tests/test_linked_list.py#L17)의 `_backward_data`에서도 `lst._tail.prev`를 에러 없이 직접 읽고 있습니다.)
* 파이썬 커뮤니티에서는 이를 **"We are all consenting adults here (우리는 모두 판단력 있는 성인이다)"**라는 철학으로 부릅니다. 언어로 강제 잠금을 걸지 않는 대신, `_` 하나로 *"이건 내부용이니 밖에서 건드리지 말자"*는 신호만 줍니다.
  *(참고: 모듈 레벨에서 `from module import *`를 할 때 `_`로 시작하는 이름을 빼주는 정도의 동작만 있고, 클래스 속성 접근은 막지 않습니다.)*

#### 참고: 언더바 두 개(`__name`)는 조금 다릅니다
* `__head`처럼 앞에 `_`를 **2개** 붙이면(뒤에는 2개 안 붙고), 파이썬이 **이름 맹글링(Name Mangling)**을 해서 실제 속성 이름을 `_클래스명__head`로 바꿔버립니다.
* 그래서 `lst.__head`라고 치면 `AttributeError`가 나긴 하지만, 이것도 `lst._DoublyLinkedList__head`로 치면 여전히 접근할 수 있어서 진짜 `private`는 아닙니다. 주로 상속 시 이름 충돌 방지용으로 쓰며, 일반 비공개 관례는 `_` **1개**를 씁니다.
