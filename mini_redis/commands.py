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
