# 0028 · tException has occurred: ModuleNotFoundError
No mo

## Q. tException has occurred: ModuleNotFoundError
No module named 'mini_redis'
  File "C:\Users\alsgu\Dev\Codyssey\B5-1\tests\test_hash_map.py", line 5, in <module>
    from mini_redis.hash_map import HashMap, fnv1a_32
ModuleNotFoundError: No module named 'mini_redis' 테스트쪽 디버깅인데, 어떤설정을 해줘야하지?

---

### 원인
`tests/test_hash_map.py` 파일을 연 채로 그냥 `F5`(Python File 실행)를 누르면, 파이썬이 프로젝트 루트(`B5-1`)가 아니라 **그 파일이 들어있는 `tests/` 폴더**를 모듈 탐색 경로(`sys.path`)로 잡습니다. 그래서 한 단계 위에 있는 `mini_redis`를 못 찾는 것입니다.
*(터미널에서 `py -3 -m unittest`로 실행할 때는 `-m` 옵션 때문에 현재 작업 폴더인 루트가 경로에 들어가서 잘 됩니다.)*

---

### 해결 방법 (둘 중 편한 쪽을 쓰세요)

#### 방법 1: VS Code 왼쪽 `Testing` 탭 이용 (가장 간단, 설정 파일 안 생김)
1. VS Code 왼쪽 사이드바의 **삼각플라스크(Testing)** 아이콘 클릭
2. **Configure Python Tests** → **`unittest`** → 테스트 폴더 **`tests`**(또는 `.`) → 패턴 **`test_*.py`** 선택
3. 이제 코드 편집기에서 각 `def test_...:` 왼쪽 줄 번호 옆에 생기는 **디버그 아이콘(Debug Test)**을 누르면 프로젝트 루트 기준으로 바로 디버깅됩니다.

#### 방법 2: `F5`로 현재 테스트 파일을 바로 디버깅 (`.vscode/launch.json`)
`Run and Debug` 패널(`Ctrl + Shift + D`) → **create a launch.json file** → **Python Debugger** → **Python File**을 만든 뒤, **`"env": { "PYTHONPATH": "${workspaceFolder}" }`** 한 줄을 넣어주면 됩니다:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Current File",
      "type": "debugpy",
      "request": "launch",
      "program": "${file}",
      "console": "integratedTerminal",
      "env": {
        "PYTHONPATH": "${workspaceFolder}"
      }
    }
  ]
}
```
*(또는 `"program": "${file}"` 대신 `"module": "unittest"`, `"args": ["-v"]`로 두면 `py -3 -m unittest -v`와 완전히 똑같이 실행됩니다. 참고로 현재 `.gitignore`에 `.vscode/`가 빠져 있으므로, `.vscode/` 폴더를 만드셨다면 커밋할 때 섞이지 않게 주의하세요!)*
