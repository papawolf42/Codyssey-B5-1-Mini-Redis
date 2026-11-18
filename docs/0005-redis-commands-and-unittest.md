# 0005 · 기본 명령어 10개와 unittest 개념

## Q. SET, GET, DEL, EXISTS 등 명령어는 각각 무슨 기능이고, unittest는 뭔가요?

---

### 1. 명령어 10개 완벽 정리

명령어가 많아 보여도 결국 **"넣고, 꺼내고, 지우고, 세어보고, 유통기한 거는 것"** 10개뿐입니다.

#### ① 기본 데이터 다루기 (6개)
| 명령어 | 뜻 | 실행 예시 | 출력 결과 | 내부 동작 |
|---|---|---|---|---|
| `SET key value` | 값 저장 (덮어쓰기) | `SET user:1 "Alice"` | `OK` | HashMap 저장 + DLL 맨 앞(MRU) 이동 + 메모리 넘치면 LRU 제거 |
| `GET key` | 값 꺼내기 | `GET user:1` | `"Alice"` (없으면 `(nil)`) | 만료 확인 → 있으면 반환 후 DLL 맨 앞(MRU) 이동 |
| `DEL key` | 키 삭제 | `DEL user:1` | `(integer) 1` (없었으면 `0`) | HashMap, DLL, 힙, used_memory 모두에서 제거 |
| `EXISTS key` | 존재하는가? | `EXISTS user:1` | `(integer) 1` 또는 `0` | 만료 안 된 키가 있으면 1, 없으면 0 (LRU 순서 변경 안 함) |
| `DBSIZE` | 총 몇 개 저장됨? | `DBSIZE` | `(integer) 2` | 현재 살아있는 전체 키 개수 반환 (LRU 순서 변경 안 함) |
| `KEYS` | 저장된 키 이름 전부 보기 | `KEYS` | `1. "user:2"` … | 모든 키 목록 출력 (순서 상관없음, 비어있으면 `(empty array)`) |

#### ② 메모리 관리하기 (2개)
| 명령어 | 뜻 | 실행 예시 | 출력 결과 |
|---|---|---|---|
| `CONFIG SET maxmemory n` | 최대 메모리 크기 설정(바이트) | `CONFIG SET maxmemory 30` | `OK` (`0`이면 무제한) |
| `INFO memory` | 메모리 현황판 보기 | `INFO memory` | `used_memory:22`<br>`maxmemory:30`<br>`evicted_keys:1` |

#### ③ 유통기한(TTL) 걸기 (2개)
| 명령어 | 뜻 | 실행 예시 | 출력 결과 의미 |
|---|---|---|---|
| `EXPIRE key seconds` | n초 뒤 자동 삭제 예약 | `EXPIRE user:2 3` | `(integer) 1` (키가 없으면 `0`) |
| `TTL key` | 남은 시간(초) 확인 | `TTL user:2` | • **양수 N**: N초 남음<br>• **`-1`**: 키는 있는데 유통기한 없음(영구)<br>• **`-2`**: 없는 키이거나 이미 만료됨 |

---

### 2. unittest(단위 테스트)란 무엇인가요?

코드를 조금 수정한 뒤 기능이 잘 돌아가는지 매번 키보드로 일일이 타이핑해서 확인할 수는 없습니다.  
파이썬 내장 라이브러리인 **`unittest`**는 **"자동 확인 버튼"**입니다.

```python
# tests/test_simple.py
import unittest

class TestExample(unittest.TestCase):
    def test_add(self):
        result = 1 + 2
        self.assertEqual(result, 3)  # "결과가 3이어야 합격!"
```

터미널에서 `py -3 -m unittest -v` 한 줄만 치면:
- 모든 검사를 0.1초 만에 실행하고,
- 하나라도 틀리면 어느 줄에서 왜 틀렸는지(빨간불) 정확히 짚어줍니다.
