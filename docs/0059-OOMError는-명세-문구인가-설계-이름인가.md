# 0059 · `OOMError`는 명세에 있는 이름일까, 우리 설계 이름일까?

## Q. `OOMError`라는 이름은 `instruction.md`에 나오는 건가요?

---

### 1. 명세에 나오는 부분 vs 우리가 지은 이름

- **`instruction.md`에 나와 있는 것 (상황과 출력 문구):**
  - **4-3장:** 키+값 하나 자체가 `maxmemory`를 넘으면 저장하지 않고 **OOM(Out Of Memory) 에러**를 출력한다.
  - **4-5장:** 그럴 때 화면에 출력할 정확한 문구 → `(error) OOM command not allowed when used_memory > 'maxmemory'`
- **우리 설계에서 지은 이름 (`OOMError`):**
  - 파이썬 예외 클래스 이름인 `class OOMError(Exception):` 자체는 명세에 적힌 이름이 아니라 **우리 계획(`0004-b5-1-daily-plan.md`)에서 만든 이름**입니다.

---

### 2. 왜 굳이 `OOMError` 예외를 따로 만들었을까요?

**“창고(`store.py`)와 안내 데스크(`commands.py`)의 역할을 깔끔하게 나누기 위해서”**입니다!

- **창고(`store.py`):** Redis 출력 문자열 문구를 몰라도 되게, 용량 초과 시 그냥 `raise OOMError()`로 **"공간 꽉 찼어! 저장 거부!"**라는 신호만 위로 던집니다.
- **안내 데스크(`commands.py`):** 그 `OOMError` 신호를 받아서 사용자에게 보여줄 공식 문자열 `(error) OOM command not allowed when used_memory > 'maxmemory'`로 바꿔 출력해 줍니다.

이렇게 나누어 두면 `store.py`는 순수 파이썬 데이터 로직에만 집중할 수 있어 코드가 훨씬 깔끔해집니다.
