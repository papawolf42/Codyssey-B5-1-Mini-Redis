"""명령어 입력을 토큰으로 나누는 동작을 검증한다."""

import unittest

from mini_redis.commands import tokenize


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
