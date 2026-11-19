# 0021 · self.assertIsNone(lst.remove_front()) 이 함수는 뭐야?

## Q. self.assertIsNone(lst.remove_front()) 이 함수는 뭐야?

---

`unittest.TestCase`에서 제공하는 **"값이 `None`인지 검증하는 테스트 메서드"**입니다.

* **동작:** 괄호 안의 `lst.remove_front()` 결과가 **`is None`인지** 확인합니다.
  * `None`이면 통과
  * `None`이 아닌 값(`Node`, `0`, `""`, `False` 등)이 나오면 테스트 실패(`AssertionError`)로 처리합니다.
* **일반 `assert`와 차이:** `assert lst.remove_front() is None`과 기능은 같지만, `assertIsNone`을 쓰면 실패했을 때 `unittest`가 실제 반환값이 무엇이었는지 더 깔끔한 오류 메시지로 보여줍니다.
* **왜 `assertEqual(..., None)` 대신 쓰나요?:** 파이썬에서 `None` 비교는 값 비교(`==`)가 아니라 객체 정체성 비교(`is None`)가 표준(PEP 8)이기 때문입니다.

즉, [test_linked_list.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/tests/test_linked_list.py#L26-L32)의 이 줄은 **"빈 리스트에서 `remove_front()`를 호출했을 때 에러가 나거나 더미 노드를 빼지 않고 정확히 `None`을 돌려주는지"** 확인하는 테스트입니다.
