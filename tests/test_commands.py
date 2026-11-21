"""명령어 입력을 토큰으로 나누는 동작을 검증한다."""

import unittest

from mini_redis.commands import execute, tokenize
from mini_redis.store import MiniRedis


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
    """execute의 출력 형식(C1·C6)과 에러 문자열(C3·C5)을 검증한다."""

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

    def test_spec_example_string_part(self):
        store = MiniRedis()
        store.config_set_maxmemory(30)  # CONFIG 명령은 7-c에서 붙는다.
        self.assertOutputs(store, (
            ('SET user:1 "Alice"', "OK"),
            ('SET user:2 "Bob"', "OK"),
            ('SET user:3 "Charlie"', "OK"),
            ("GET user:1", "(nil)"),
        ))
        lines = execute(store, "KEYS").split("\n")  # 순서는 해시 버킷 순서다.
        self.assertEqual([line[:3] for line in lines], ["1. ", "2. "])
        self.assertEqual(sorted(line[3:] for line in lines), ['"user:2"', '"user:3"'])

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
                     "DBSIZE x", "KEYS user:*", "KEYS * *"):
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
