"""Mini Redis CLI 실행 진입점."""


def main():
    """mini-redis> 프롬프트를 띄우고 사용자 입력을 반복 처리한다."""
    while True:
        try:
            line = input("mini-redis> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        if line.lower() in ("exit", "quit"):
            break

        print(line)


if __name__ == "__main__":
    main()
