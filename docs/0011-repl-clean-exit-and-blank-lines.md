# 0011 · main.py의 줄바꿈 print()와 if not line 조건의 비밀

## Q. main.py의 예외 처리 직후 `print()`는 왜 있고, `if not line:`에서 line이 False가 되는 조건은 무엇인가요?

---

### 1. `except (EOFError, KeyboardInterrupt):` 직후의 `print()`는 왜 필요한가요?

```python
try:
    line = input("mini-redis> ").strip()
except (EOFError, KeyboardInterrupt):
    print()  # <--- 이 줄!
    break
```

`input("mini-redis> ")`는 프롬프트 문자열을 출력할 때 **줄바꿈 없이 커서를 글자 바로 옆에 세워둡니다.**

```text
mini-redis> █
```

- 평소처럼 명령어를 입력하고 `Enter`를 치면, 터미널이 엔터 입력에 반응해 자동으로 다음 줄로 커서를 내려줍니다.
- 하지만 사용자가 **`Ctrl + C`**를 누르거나 **`Ctrl + D`**(Linux/macOS)를 누를 때는 **`Enter`를 친 게 아니므로 커서가 다음 줄로 내려가지 않고 프롬프트 바로 옆에 멈춰 있습니다.**

이때 빈 `print()` 없이 바로 `break`로 프로그램을 끝내버리면, 원래 터미널 쉘 프롬프트(`PS C:\...>`)가 보기 흉하게 같은 줄에 달라붙어 버립니다.

#### ① 빈 `print()`가 없을 때 (줄바꿈 없음)
```text
mini-redis> PS C:\Users\alsgu\Dev\Codyssey\B5-1>
```

#### ② 빈 `print()`가 있을 때 (줄바꿈 `\n` 1번 출력)
```text
mini-redis>
PS C:\Users\alsgu\Dev\Codyssey\B5-1>
```

즉, **원래 쉘로 돌아갈 때 프롬프트가 새 줄에 깔끔하게 시작하도록 커서를 한 칸 내려주는 용도**입니다. (인자 없는 `print()`는 기본적으로 `\n`만 출력합니다.)

---

### 2. `if not line: continue` 에서 `line`이 False가 되는 조건은?

> "엔터만 쳐서 개행만 들어온 것 말고 또 있나요? 개행이 들어오면 line은 False가 되나요?"

코드의 순서를 따라가 보면 명확합니다:

```python
line = input("mini-redis> ").strip()

if not line:
    continue
```

#### ① 파이썬에서 문자열이 False로 취급되는 규칙 (Falsy)
파이썬에서는 오직 **길이가 0인 빈 문자열 `""`만 `False`**로 평가되고, 글자가 1글자라도 들어있으면 무조건 `True`입니다.
- `bool("")` → `False`
- `bool("a")` → `True`
- `bool(" ")` (공백 1개) → `True`!
- `bool("\n")` (개행 1개) → `True`!

#### ② 그렇다면 엔터만 쳤을 때 왜 `line`이 빈 문자열이 될까?
- `input()` 함수 자체가 동작할 때, 사용자가 친 마지막 **엔터(`\n`)를 이미 떼어내고 돌려줍니다.**  
  따라서 아무것도 안 치고 엔터만 치면 `input()`의 반환값 자체가 이미 `""` (0글자)입니다.
- 여기에 추가로 뒤에 붙은 **`.strip()`**이 양쪽 끝의 공백 문자들을 싹 지워줍니다.

#### ③ 따라서 `if not line:`에 걸리는 입력들
1. **아무것도 안 치고 엔터만 친 경우:**  
   `input()`이 `""` 반환 → `.strip()` 거쳐도 `""` → `len == 0` (False)
2. **스페이스바(공백)나 탭(`\t`)만 치고 엔터를 친 경우:**  
   예: `"   "` 입력 → `.strip()`이 공백을 다 지워서 `""`로 변환 → `len == 0` (False)
3. **스페이스 여러 개 + 탭 여러 개 조합:**  
   전부 `.strip()`에 의해 사라져서 `""`가 됨 → (False)

결과적으로 **"의미 있는 글자가 하나도 입력되지 않은 모든 헛손질(엔터, 스페이스, 탭)"**을 걸러내어, 쓸데없이 명령어 처리를 하지 않고 다음 프롬프트로 깔끔하게 넘기는 안전장치입니다.
