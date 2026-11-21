"""Mini Redis 명령어를 처리한다."""


def tokenize(line):
    """공백을 건너뛰며 명령과 인자를 하나씩 읽는다."""
    tokens = []
    position = 0

    while position < len(line):
        if line[position].isspace():
            position += 1
            continue

        token, position = _read_token(line, position)
        tokens.append(token)

    return tokens


def _read_token(line, position):
    """토큰 하나와 다음 위치를 반환한다. 따옴표 안의 공백은 값에 포함한다."""
    parts = []

    while position < len(line):
        character = line[position]
        if character.isspace():
            break

        if character == '"':
            closing_quote = line.find('"', position + 1)
            if closing_quote == -1:
                raise ValueError("큰따옴표가 닫히지 않았습니다.")

            parts.append(line[position + 1:closing_quote])
            position = closing_quote + 1
            continue

        parts.append(character)
        position += 1

    return "".join(parts), position


# (명령 이름, 인자 수). dict를 쓸 수 없으니 짧은 튜플 표를 앞에서부터 훑는다.
_ARG_COUNTS = (
    ("SET", 2),
    ("GET", 1),
    ("DEL", 1),
    ("EXISTS", 1),
    ("DBSIZE", 0),
    ("KEYS", 0),
)


def _arg_count_of(command):
    """명령의 인자 수를 반환한다. 모르는 명령이면 None을 반환한다."""
    for name, count in _ARG_COUNTS:
        if name == command:
            return count
    return None


def _integer(number):
    """정수 응답: (integer) N"""
    return f"(integer) {number}"


def _bulk(value):
    """문자열 응답: 값이 없으면 (nil), 있으면 큰따옴표로 감싼다."""
    if value is None:
        return "(nil)"
    return f'"{value}"'


def _array(items):
    """목록 응답: 1부터 번호를 붙인 줄들. 비었으면 (empty array)."""
    if not items:
        return "(empty array)"
    lines = []
    for number, item in enumerate(items, start=1):
        lines.append(f'{number}. "{item}"')
    return "\n".join(lines)


def execute(store, line):
    """명령 한 줄을 실행해 화면에 찍을 문자열을 반환한다.

    판정 순서는 토큰화 → 모르는 명령 → 인자 수 → 실행이다.
    에러 메시지에는 사용자가 입력한 이름을 대소문자 그대로 쓴다.
    """
    try:
        tokens = tokenize(line)
    except ValueError:
        return "(error) ERR syntax error"
    if not tokens:
        return ""

    name = tokens[0]
    command = name.upper()
    args = tokens[1:]
    if command == "KEYS" and args == ["*"]:
        args = []  # 패턴 매칭은 하지 않지만, Redis 습관대로 친 KEYS *는 KEYS로 받는다.

    expected = _arg_count_of(command)
    if expected is None:
        return f"(error) ERR unknown command '{name}'"
    if len(args) != expected:
        return f"(error) ERR wrong number of arguments for '{name}' command"

    if command == "SET":
        store.set(args[0], args[1])
        return "OK"
    if command == "GET":
        return _bulk(store.get(args[0]))
    if command == "DEL":
        return _integer(store.delete(args[0]))
    if command == "EXISTS":
        return _integer(store.exists(args[0]))
    if command == "DBSIZE":
        return _integer(store.dbsize())
    if command == "KEYS":
        return _array(store.keys())
