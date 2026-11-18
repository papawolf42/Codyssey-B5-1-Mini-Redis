# 0009 · EOFError와 KeyboardInterrupt의 내부 동작 원리

## Q. main.py에서 `except (EOFError, KeyboardInterrupt):`는 왜 넣었고, 내부에서는 실제로 어떤 일이 일어나나요?

---

### 1. 왜 이 예외 처리를 넣었나요?

`main.py`의 `while True:` 루프는 `input("mini-redis> ")`로 사용자의 입력을 계속 기다립니다.  
사용자가 정상적으로 `exit`나 `quit`을 치지 않고 **강제 종료 단축키**를 누르거나 **파이프로 입력을 전달**할 때, 붉은색 트레이스백(Traceback) 에러 메시지 없이 조용하고 깔끔하게 프로그램을 종료하기 위해 넣었습니다.

```python
try:
    line = input("mini-redis> ").strip()
except (EOFError, KeyboardInterrupt):
    print()   # 프롬프트 줄에서 깔끔하게 줄바꿈
    break     # 루프 탈출 -> 정상 종료
```

---

### 2. 직접 이 에러를 일으키는 방법

1. **`KeyboardInterrupt` 일으키기:**
   - `mini-redis> ` 입력 대기 상태에서 **`Ctrl + C`** 입력
2. **`EOFError` 일으키기:**
   - **Windows (PowerShell / CMD):** **`Ctrl + Z`** 누른 뒤 **`Enter`**
   - **macOS / Linux / Git Bash:** 빈 줄에서 **`Ctrl + D`**
   - **파이프 입력:** `"hello" | py -3 main.py` (내용을 다 읽은 뒤 다음 `input()`에서 입력이 끝나 발생)

---

### 3. OS와 파이썬 내부에서는 실제로 무슨 일이 일어날까?

> "Ctrl+C는 시그널이 날아가는 걸로 알고, EOF는 눈에 안 보이는 캐리지 리턴 같은 특수 문자가 들어오는 건가요?"

결론부터 말하면 **Ctrl+C는 시그널이 맞고, EOF는 문자가 아니라 "읽은 데이터가 0바이트"라는 커널 상태**입니다.

#### ① Ctrl + C (`KeyboardInterrupt`): OS 시그널 방식
1. **OS / 터미널 레벨:**  
   사용자가 `Ctrl + C`를 누르면 터미널 드라이버나 콘솔 호스트가 가로채서 프로세스에 신호를 보냅니다.
   - Linux/macOS: `SIGINT` 시그널 전달
   - Windows: `CTRL_C_EVENT` 콘솔 제어 이벤트 발생
2. **Python 인터프리터 레벨:**  
   파이썬은 실행 시 기본적으로 이 신호를 가로채는 핸들러를 등록해 둡니다. 신호가 오면 프로세스를 바로 강제 종료하지 않고, 내부 플래그를 켠 뒤 **`KeyboardInterrupt` 예외를 발생(raise)**시킵니다.
   - *참고: `KeyboardInterrupt`는 일반 `Exception`이 아닌 `BaseException`을 직접 상속하므로, `except Exception:`으로는 잡히지 않고 명시해야 잡힙니다.*

#### ② EOF (`EOFError`): 특수 문자가 아니라 "0바이트" 읽기 상태
EOF(End Of File)는 `\r`, `\0` 같은 **특수 문자가 들어오는 것이 아닙니다.**  
운영체제의 읽기 시스템 콜(`read()` / `ReadFile()`) 결과가 **0바이트(더 이상 읽을 데이터가 없음)**라는 "상태"를 뜻합니다.

- **Enter만 친 빈 줄:**  
  실제로는 줄바꿈 문자 `"\n"` (1바이트)가 전달됩니다. `input()`은 `"\n"`을 읽은 뒤 끝의 개행을 잘라내어 빈 문자열 `""`을 반환합니다.
- **EOF인 경우:**  
  읽은 결과 자체가 아예 0바이트(길이 0)입니다. `input()` 입장에서는 *"엔터 친 빈 줄(`\n`)이 아니라 입력 통로 자체가 닫혔구나!"*라고 구분하기 위해 **`EOFError`를 던집니다.**
  *(참고: `sys.stdin.readline()`은 EOF일 때 에러 대신 빈 문자열 `""`을 돌려주지만, `input()`은 개행을 잘라내므로 빈 줄과 구분하기 위해 예외를 발생시키도록 설계되었습니다.)*

#### ③ Ctrl+D / Ctrl+Z는 왜 EOF가 될까?
- **macOS / Linux (`Ctrl + D`):**  
  터미널 드라이버에게 *"현재 버퍼에 있는 걸 즉시 프로그램으로 보내라(flush)"*는 신호입니다. 아무것도 없는 빈 줄에서 누르면 보낼 데이터가 0바이트이므로 프로그램이 0바이트를 읽게 되어 EOF가 됩니다.
- **Windows (`Ctrl + Z + Enter`):**  
  Windows 콘솔 호스트가 줄 맨 앞의 `Ctrl+Z`를 "표준 입력의 끝" 표시로 해석하여, 프로그램의 읽기 요청에 0바이트를 돌려줍니다.
- **파이프/파일 (`echo "hello" | py main.py`):**  
  앞쪽 프로그램이 데이터를 다 보내고 파이프를 닫으면, OS 커널이 0바이트를 반환하므로 동일하게 EOF가 됩니다.

---

### 4. 한눈에 요약

| 구분 | 발생 원인 | 내부 메커니즘 | 파이썬의 반응 |
|---|---|---|---|
| **`KeyboardInterrupt`** | 사용자가 `Ctrl+C` 입력 | OS 시그널 (`SIGINT`, `CTRL_C_EVENT`) 전달 | 파이썬이 잡아서 `KeyboardInterrupt` 예외 발생 |
| **`EOFError`** | `Ctrl+Z+Enter`(Win), `Ctrl+D`(Mac/Linux), 파이프 끝 | 문자가 아니라 OS가 **0바이트 반환** (스트림 종료) | `input()`이 빈 줄(`\n`)과 구분하기 위해 `EOFError` 예외 발생 |
