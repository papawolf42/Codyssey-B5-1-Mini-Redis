# 0008 · instruction.md 내의 CLI/REPL 명세 위치와 분석

## Q. main.py의 CLI/REPL 구현 명세는 instruction.md 어디에 적혀 있나요?

---

### 1. instruction.md 원문 명세 위치

과제 요구사항 문서([instruction.md](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/instruction.md))에서 CLI와 REPL 관련 규칙은 다음 4개 항목에 명시되어 있습니다:

#### ① 2. 최종 결과물 → CLI 인터페이스 (64~68줄)
> - 사용자가 명령어를 입력하면 즉시 실행 결과를 확인할 수 있는 REPL 환경
> - 명령어 파싱, 실행, 결과 출력이 반복적으로 동작

#### ② 4-5. 에러 처리 표준 + CLI 인터페이스 → CLI (204~209줄)
> - `mini-redis>` 프롬프트 출력
> - 사용자 입력을 읽고 명령어 파싱 및 실행
> - `exit` 또는 `quit`으로 종료 가능

#### ③ 7. 제약 사항 → 기능 범위 (267~270줄)
> - 네트워크 통신은 구현하지 않는다. (오직 CLI)

#### ④ 8. 결과 예시 → 실행 예시 (280~282줄)
> ```text
> mini-redis> CONFIG SET maxmemory 30
> OK
> ```
> *(프롬프트 `mini-redis>` 뒤에 공백 1칸이 포함됨)*

---

### 2. 우리가 main.py에 반영한 세부 구현 규칙

1. **대소문자 무시 종료:** 사용자가 `exit`, `quit`, `EXIT`, `QUIT` 어떤 형태로 입력해도 정상 종료.
2. **빈 줄 처리:** 아무것도 입력하지 않고 Enter만 치면 무시하고 다음 프롬프트 대기.
3. **예외 처리:** `Ctrl+C`(`KeyboardInterrupt`)나 `Ctrl+Z`(`EOFError`)를 눌렀을 때 터미널에 붉은색 트레이스백 에러를 뿜지 않고, 깔끔하게 줄바꿈 후 정상 종료(`exit code 0`).
