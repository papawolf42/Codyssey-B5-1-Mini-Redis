# 0012 · 이거 doc string을 꼭 써야해?

## Q. 이거 doc string을 꼭 써야해?

---

결론부터 말씀드리면 **"모든 메서드에 다 써야 하는 건 아니지만, 핵심 클래스·함수에는 주석 또는 docstring 중 하나가 필수"**입니다.

---

### 1. 공식 요구사항 기준
[instruction.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/instruction.md#L262-L266)의 제약 사항에 이렇게 적혀 있습니다:
> **핵심 클래스/함수에는 주석 또는 docstring을 작성한다.**

즉:
* **핵심 클래스/함수**(`Node`, `DoublyLinkedList`, 주요 연산 메서드)에는 `#` 주석이든 `"""..."""` docstring이든 설명이 있어야 스펙을 만족합니다.
* 반대로 `Node.__init__`, `DoublyLinkedList.__init__`, `size()`, `__iter__` 같은 **코드만 봐도 뻔한 메서드**까지 일일이 docstring을 달 필요는 없습니다.

### 2. 왜 지금 코드에 많이 달려 있나?
[0004-b5-1-daily-plan.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/docs/0004-b5-1-daily-plan.md#L17)에서 **파이썬 3.8 호환을 위해 타입 힌트를 빼기로** 했기 때문에, 인자/반환값과 "왜 O(1)인지"를 docstring으로 남기는 쪽으로 맞춰 놓은 것입니다.

---

### 어떻게 정리하면 좋을까요?
지금 [linked_list.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/linked_list.py)에서 아래처럼 **자명한 docstring은 빼고 핵심만 남기면** 훨씬 깔끔하고 읽기 편해집니다:
* **유지:** 모듈 docstring 1줄, `Node`·`DoublyLinkedList` 클래스 docstring(더미 노드/O(1) 이유), 앞으로 추가될 핵심 메서드(`_link_after`, `_unlink`, `move_to_front` 등)에 짧은 1줄
* **제거 가능:** `Node.__init__`, `DoublyLinkedList.__init__`, `size`, `__iter__`, 테스트 파일 내 자명한 docstring

자명한 메서드의 docstring을 덜어내고(이후 백업분도 맞춰서) 훨씬 간결하게 정리할까요?
