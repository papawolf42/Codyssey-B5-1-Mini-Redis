# 0042 · 그럼 capacity속성이 없어지는거네? 메소드로 남고?

## Q. 그럼 capacity속성이 없어지는거네? 메소드로 남고?

---

**겉으로 쓰는 입장에서는 여전히 속성(`hm.capacity`) 그대로입니다!**

---

### `@property`의 동작 방식
코드는 `def capacity(self):` 형태로 적지만, 위에 **`@property`**를 붙이면 파이썬이 이를 **메서드 호출이 아니라 속성 접근처럼** 바꿔줍니다.

```python
hm = HashMap()
hm.capacity     # 괄호 없이 속성처럼 접근 → 자동으로 len(self._buckets) 실행 → 8 반환!
hm.capacity()   # 오히려 괄호를 붙이면 TypeError 발생
```

* **장점:**
  1. 외부/테스트에서는 기존과 똑같이 `hm.capacity`로 읽습니다.
  2. 실수로 바깥에서 `hm.capacity = 99`라고 덮어쓰는 것도 막아줍니다(읽기 전용).
  3. 저장은 `self._buckets` 한 곳만 하므로 단일 진실이 유지됩니다.

---

### 다만 학습·설명 관점에서는
만약 *"`@property` 문법까지 설명하기보다는 그냥 평범한 변수 `self.capacity`가 더 직관적이다"* 싶으시면:
* `__init__`에 `self.capacity = capacity`를 그대로 두고,
* `_index`만 `fnv1a_32(key) % self.capacity`로 바꾸는 **방법 2**도 충분히 깔끔합니다! (대신 다음 `3-a`에서 버킷을 2배로 바꿀 때 `self.capacity`도 같이 `*= 2` 해주면 됩니다.)

두 가지 중 어느 쪽으로 적용할까요?
1. **`@property` 방식** (완전한 단일 진실 + `hm.capacity` 읽기 전용 속성)
2. **`self.capacity` 변수 유지 + `_index`도 `self.capacity` 사용** (가장 단순한 문법)
