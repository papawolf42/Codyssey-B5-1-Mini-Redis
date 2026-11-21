"""Mini Redis 명령어를 처리한다."""

from mini_redis.store import OOMError


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


# 에러 문자열은 스펙 글자 그대로 여기에만 둔다. {name}에는 사용자가 입력한 명령 이름이 들어간다.
_SYNTAX_ERROR = "(error) ERR syntax error"
_UNKNOWN_COMMAND = "(error) ERR unknown command '{name}'"
_WRONG_ARGS = "(error) ERR wrong number of arguments for '{name}' command"
_NOT_INTEGER = "(error) ERR value is not an integer or out of range"
_OOM = "(error) OOM command not allowed when used_memory > 'maxmemory'"

# (명령 이름, 인자 수). dict를 쓸 수 없으니 짧은 튜플 표를 앞에서부터 훑는다.
_ARG_COUNTS = (
    ("SET", 2),
    ("GET", 1),
    ("DEL", 1),
    ("EXISTS", 1),
    ("DBSIZE", 0),
    ("KEYS", 0),
    ("EXPIRE", 2),
    ("TTL", 1),
    ("CONFIG", 3),
    ("INFO", 0),
)


def _arg_count_of(command):
    """명령의 인자 수를 반환한다. 모르는 명령이면 None을 반환한다."""
    for name, count in _ARG_COUNTS:
        if name == command:
            return count
    return None


def _parse_int(text):
    """맨 앞 '-'와 0~9로만 된 글자를 정수로 바꾼다. 아니면 None을 반환한다.

    int()는 '1_000', '+5', ' 5'도 받아 주므로 바로 쓰지 않고 먼저 걸러 낸다.
    """
    digits = text[1:] if text.startswith("-") else text
    if digits == "":
        return None
    for character in digits:
        if character < "0" or character > "9":
            return None
    return int(text)


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


def _drop_optional_arg(command, args):
    """KEYS *와 INFO memory는 KEYS, INFO와 같은 결과이므로 그 인자를 뺀다."""
    if command == "KEYS" and args == ["*"]:
        return []  # 패턴 매칭은 하지 않지만, Redis 습관대로 친 KEYS *는 받아 준다.
    if command == "INFO" and len(args) == 1 and args[0].lower() == "memory":
        return []
    return args


def _set(store, args):
    """SET key value. 한도보다 큰 값이면 OOM 에러를 반환한다."""
    try:
        store.set(args[0], args[1])
    except OOMError:
        return _OOM
    return "OK"


def _expire(store, args):
    """EXPIRE key seconds. 초가 정수가 아니거나 너무 크면 정수 에러를 반환한다."""
    seconds = _parse_int(args[1])
    if seconds is None:
        return _NOT_INTEGER
    try:
        return _integer(store.expire(args[0], seconds))
    except OverflowError:  # 지금 시각 + 아주 큰 초는 실수(float) 범위를 넘는다.
        return _NOT_INTEGER


def _config(store, name, args):
    """CONFIG SET maxmemory n만 지원한다. 다른 형태는 인자 수 에러로 처리한다."""
    if args[0].upper() != "SET" or args[1].lower() != "maxmemory":
        return _WRONG_ARGS.format(name=name)
    limit = _parse_int(args[2])
    if limit is None or limit < 0:
        return _NOT_INTEGER
    store.config_set_maxmemory(limit)
    return "OK"


def _info(store):
    """INFO memory의 세 줄을 만든다."""
    used, maxmemory, evicted = store.info_memory()
    return f"used_memory:{used}\nmaxmemory:{maxmemory}\nevicted_keys:{evicted}"


def execute(store, line):
    """명령 한 줄을 실행해 화면에 찍을 문자열을 반환한다.

    판정 순서는 토큰화 → 모르는 명령 → 인자 수 → 정수 → OOM이다.
    에러 메시지에는 사용자가 입력한 이름을 대소문자 그대로 쓴다.
    """
    try:
        tokens = tokenize(line)
    except ValueError:
        return _SYNTAX_ERROR
    if not tokens:
        return ""

    name = tokens[0]
    command = name.upper()
    args = _drop_optional_arg(command, tokens[1:])

    expected = _arg_count_of(command)
    if expected is None:
        return _UNKNOWN_COMMAND.format(name=name)
    if len(args) != expected:
        return _WRONG_ARGS.format(name=name)

    if command == "SET":
        return _set(store, args)
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
    if command == "EXPIRE":
        return _expire(store, args)
    if command == "TTL":
        return _integer(store.ttl(args[0]))
    if command == "CONFIG":
        return _config(store, name, args)
    if command == "INFO":
        return _info(store)
