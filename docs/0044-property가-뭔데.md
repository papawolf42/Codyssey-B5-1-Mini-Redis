# 0044 · @property가 뭔데?

## Q. @property가 뭔데?

---

**`@property`는 "함수(메서드)를 일반 변수(속성)처럼 괄호 `()` 없이 읽을 수 있게 바꿔주는 파이썬 기본 기능(내장 데코레이터)"입니다.**

---

### 쉬운 예시로 보면 바로 이해됩니다
```python
class Box:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @property
    def area(self):
        return self.width * self.height
```

* 원래 메서드라면 `box.area()`라고 **괄호**를 붙여 불러야 합니다.
* 하지만 위에 `@property`를 붙여두면:
  1. **`box.area`** — 변수처럼 괄호 없이 읽어도 자동으로 `width * height`를 계산해 돌려줍니다.
  2. **`width`가 바뀌어도 항상 최신 값** — 넓이 변수를 따로 수정할 필요가 없습니다.
  3. **읽기 전용 보호** — 밖에서 `box.area = 999`처럼 값을 마음대로 덮어쓰려 하면 `AttributeError`로 막아줍니다.

*(참고: `@`로 시작하는 문법을 **데코레이터**라고 부르며, 바로 아래 함수를 감싸 성격을 바꿔주는 표시입니다. `@property`는 파이썬 기본 내장 기능이라 따로 `import`할 것도 없습니다.)*

---

### 우리 `HashMap`에 적용하면
```python
@property
def capacity(self):
    """현재 버킷 배열의 크기를 반환한다."""
    return len(self._buckets)
```
* 테스트나 외부 코드에서는 기존과 똑같이 **`hm.capacity`**라고 읽고,
* 내부적으로는 항상 **`len(self._buckets)`(O(1))** 하나만 참조하므로 버킷 배열과 `capacity` 숫자가 따로 놀 일이 없어집니다.

---

이렇게 `@property`로 반영하고 테스트 돌린 뒤 먼저 확인시켜 드릴까요? (아니면 바로 커밋까지 할까요?)
