"""명령어 토큰화와 실행 결과 문자열을 검증한다."""

import unittest

from mini_redis.commands import execute, tokenize
from mini_redis.store import MiniRedis


class FakeClock:
    """테스트에서 필요할 때만 시간이 흐르는 시계."""

    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


class TestTokenize(unittest.TestCase):
    def test_splits_command_and_arguments(self):
        self.assertEqual(tokenize("SET a 1"), ["SET", "a", "1"])

    def test_keeps_spaces_inside_quotes(self):
        self.assertEqual(
            tokenize('SET msg "hello world"'), ["SET", "msg", "hello world"]
        )

    def test_keeps_empty_quoted_value(self):
        self.assertEqual(tokenize('SET k ""'), ["SET", "k", ""])

    def test_keeps_adjacent_quoted_and_unquoted_parts_in_one_token(self):
        self.assertEqual(tokenize('SET k pre" x "post'), ["SET", "k", "pre x post"])

    def test_rejects_unclosed_quote(self):
        with self.assertRaises(ValueError):
            tokenize('SET k "abc')

    def test_ignores_extra_whitespace_outside_quotes(self):
        self.assertEqual(tokenize("  GET   a  "), ["GET", "a"])

    def test_empty_and_whitespace_only_lines(self):
        self.assertEqual(tokenize(""), [])
        self.assertEqual(tokenize(" \t "), [])


class TestExecute(unittest.TestCase):
    """execute의 출력 형식(C1·C6)과 에러 문자열(C2·C3·C5)을 검증한다."""

    def assertOutputs(self, store, pairs):
        """(입력 줄, 기대 출력) 쌍을 차례로 실행해 비교한다."""
        for line, expected in pairs:
            with self.subTest(line=line):
                self.assertEqual(execute(store, line), expected)

    def test_string_command_outputs(self):
        self.assertOutputs(MiniRedis(), (
            ("GET a", "(nil)"),
            ('SET a "hello world"', "OK"),
            ("GET a", '"hello world"'),
            ('SET b ""', "OK"),
            ("GET b", '""'),
            ("EXISTS a", "(integer) 1"),
            ("EXISTS missing", "(integer) 0"),
            ("DBSIZE", "(integer) 2"),
            ("DEL a", "(integer) 1"),
            ("DEL a", "(integer) 0"),
            ("DBSIZE", "(integer) 1"),
        ))

    def test_keys_numbered_list_and_star(self):
        self.assertOutputs(MiniRedis(), (
            ("KEYS", "(empty array)"),
            ("SET only 1", "OK"),
            ("KEYS", '1. "only"'),
            ("keys *", '1. "only"'),
        ))

    def test_spec_example(self):
        """스펙 8장 실행 예시. KEYS 순서만 해시 버킷 순서라 예시와 다를 수 있다."""
        clock = FakeClock()
        store = MiniRedis(clock=clock)
        self.assertOutputs(store, (
            ("CONFIG SET maxmemory 30", "OK"),
            ('SET user:1 "Alice"', "OK"),
            ('SET user:2 "Bob"', "OK"),
            ('SET user:3 "Charlie"', "OK"),
            ("GET user:1", "(nil)"),
            ("INFO memory", "used_memory:22\nmaxmemory:30\nevicted_keys:1"),
        ))
        lines = execute(store, "KEYS").split("\n")
        self.assertEqual([line[:3] for line in lines], ["1. ", "2. "])
        self.assertEqual(sorted(line[3:] for line in lines), ['"user:2"', '"user:3"'])
        self.assertEqual(execute(store, "EXPIRE user:2 3"), "(integer) 1")
        clock.advance(0.001)  # 실제로는 시간이 조금 흘러 2.999…초가 남고, 버리면 2다.
        self.assertEqual(execute(store, "TTL user:2"), "(integer) 2")
        clock.advance(3)
        self.assertOutputs(store, (
            ("GET user:2", "(nil)"),
            ("TTL user:2", "(integer) -2"),
        ))

    def test_expire_and_ttl(self):
        self.assertOutputs(MiniRedis(clock=FakeClock()), (
            ("EXPIRE missing 10", "(integer) 0"),
            ("TTL missing", "(integer) -2"),
            ("SET a 1", "OK"),
            ("TTL a", "(integer) -1"),
            ("expire a 10", "(integer) 1"),
            ("TTL a", "(integer) 10"),
            ("EXPIRE a -5", "(integer) 1"),
            ("EXISTS a", "(integer) 0"),
        ))

    def test_config_info_and_oom(self):
        self.assertOutputs(MiniRedis(), (
            ("INFO", "used_memory:0\nmaxmemory:0\nevicted_keys:0"),
            ("config set MAXMEMORY 10", "OK"),
            ("SET k 1234567890",
             "(error) OOM command not allowed when used_memory > 'maxmemory'"),
            ("EXISTS k", "(integer) 0"),
            ("info MEMORY", "used_memory:0\nmaxmemory:10\nevicted_keys:0"),
        ))

    def test_integer_errors_keep_old_state(self):
        store = MiniRedis(clock=FakeClock())
        execute(store, "SET a 1")
        for line in ("CONFIG SET maxmemory abc", "CONFIG SET maxmemory -1",
                     "CONFIG SET maxmemory 1_000", "CONFIG SET maxmemory +5",
                     'CONFIG SET maxmemory " 5"', "EXPIRE a abc", "EXPIRE a 1.5",
                     "EXPIRE a -", "EXPIRE a 1" + "0" * 400):
            with self.subTest(line=line[:40]):
                self.assertEqual(
                    execute(store, line),
                    "(error) ERR value is not an integer or out of range",
                )
        self.assertOutputs(store, (
            ("INFO", "used_memory:2\nmaxmemory:0\nevicted_keys:0"),
            ("TTL a", "(integer) -1"),
        ))

    def test_spec_errors_and_input_name_kept(self):
        self.assertOutputs(MiniRedis(), (
            ("GET", "(error) ERR wrong number of arguments for 'GET' command"),
            ("HELLO", "(error) ERR unknown command 'HELLO'"),
            ("hello a b c", "(error) ERR unknown command 'hello'"),
            ("set a 1", "OK"),
            ("gEt a", '"1"'),
            ("gEt", "(error) ERR wrong number of arguments for 'gEt' command"),
        ))

    def test_wrong_arg_count_changes_nothing(self):
        store = MiniRedis()
        for line in ("SET a", "SET a b c", "GET a b", "DEL", "EXISTS a b",
                     "DBSIZE x", "KEYS user:*", "KEYS * *", "EXPIRE a",
                     "TTL", "CONFIG SET maxmemory", "CONFIG GET maxmemory",
                     "CONFIG SET timeout 5", "INFO foo", "INFO memory extra"):
            name = line.split()[0]
            with self.subTest(line=line):
                self.assertEqual(
                    execute(store, line),
                    f"(error) ERR wrong number of arguments for '{name}' command",
                )
        self.assertEqual(execute(store, "DBSIZE"), "(integer) 0")

    def test_blank_lines_and_unclosed_quote(self):
        self.assertOutputs(MiniRedis(), (
            ("", ""),
            ("   ", ""),
            ('SET k "abc', "(error) ERR syntax error"),
            ("DBSIZE", "(integer) 0"),
        ))
