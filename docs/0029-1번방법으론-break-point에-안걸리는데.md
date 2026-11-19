# 0029 · 1번방법으론 break point에 안걸리는데 어떤식으로 디버깅하는거지?

## Q. 1번방법으론 break point에 안걸리는데 어떤식으로 디버깅하는거지?

---

Testing 패널(방법 1)을 쓸 때 브레이크포인트에 안 걸리는 원인은 보통 아래 셋 중 하나입니다.

---

### 1. `Run Test`를 누른 경우 (가장 흔함)
테스트 옆의 초록색 재생 버튼(`▶`)을 그냥 누르면 **디버거 없이 실행(Run Test)**만 합니다.
* **해결:**
  * 코드 줄 번호 옆 `▶` 버튼을 **우클릭 → `Debug Test`** 선택
  * 또는 왼쪽 **Testing(플라스크) 사이드바**에서 테스트 항목에 마우스를 올려 **재생+벌레 아이콘(`Debug Test`)** 클릭

---

### 2. 브레이크포인트가 실제 실행되는 줄에 안 찍혔거나 저장 안 됨
* 파일이 저장(`Ctrl + S`) 안 되어 있으면 디버거가 줄을 못 맞출 수 있습니다.
* 예를 들어 `fnv1a_32`를 보고 싶다면:
  1. [hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/hash_map.py#L16)의 `h ^= byte` 줄에 빨간 점(브레이크포인트)을 찍고
  2. [test_hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/tests/test_hash_map.py#L11)의 `test_standard_vectors` 옆에서 **`Debug Test`**를 실행해야 안쪽으로 들어가면서 멈춥니다.
  *(브레이크포인트가 꽉 찬 빨간 원이 아니라 **회색 빈 동그라미**로 떠 있으면 디버거가 아직 안 붙은 상태입니다.)*

---

### 3. 그래도 Testing 패널에서 계속 안 걸릴 때 (확실한 해결책)
VS Code Python 확장에서 Testing 러너가 간혹 디버거 연결을 놓치는 경우가 있습니다. 이럴 때는 **방법 2(`launch.json` + `F5`)**로 바로 디버깅하시는 게 훨씬 확실합니다:

1. `.vscode/launch.json`에 아까 적어드린 설정(`"env": { "PYTHONPATH": "${workspaceFolder}" }`)을 넣고 저장
2. [test_hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/tests/test_hash_map.py) 탭을 열어둔 상태에서 **`F5`** 클릭!
3. 이 방식은 일반 디버거가 직접 실행되므로 [hash_map.py](file:///C:/Users/alsgu/Dev/Codyssey/B5-1/mini_redis/hash_map.py#L16)에 걸어둔 브레이크포인트에서 **100% 바로 멈춥니다.**

*(참고: `.vscode/` 폴더를 만드셨다면 나중에 `git status`에 뜨니 원치 않으시면 `.gitignore`에 `.vscode/`를 추가해 두시면 됩니다.)*
