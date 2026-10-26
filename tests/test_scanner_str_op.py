import unittest
from minijava.scanner_str_op import scan_string, scan_operator
from minijava.tokens import TokenType
from minijava.diagnostics import ErrorCode


class TestScanString(unittest.TestCase):
    def ok(self, src, pos=0, line=1, col=1):
        r = scan_string(src, pos, line, col)
        self.assertIsNotNone(r[3], src)
        self.assertIsNone(r[4])
        return r

    def test_double_quoted(self):
        p, l, c, t, d = self.ok('"Ali"')
        self.assertEqual((t.type, t.lexeme), (TokenType.STRING, '"Ali"'))
        self.assertEqual((p, l, c), (5, 1, 6))

    def test_double_quoted_with_space(self):
        self.assertEqual(self.ok('"Hello World"')[3].lexeme, '"Hello World"')

    def test_single_quoted_char(self):
        self.assertEqual(self.ok("'A'")[3].lexeme, "'A'")

    def test_single_quoted_x(self):
        self.assertEqual(self.ok("'x'")[3].lexeme, "'x'")

    def test_empty_string(self):
        self.assertEqual(self.ok('""')[3].lexeme, '""')

    def test_escape_newline(self):
        self.assertEqual(self.ok(r'"Line1\nLine2"')[3].lexeme, r'"Line1\nLine2"')

    def test_escape_tab(self):
        self.assertEqual(self.ok(r'"a\tb"')[3].lexeme, r'"a\tb"')

    def test_escaped_double_quote(self):
        s = r'"He said \"Hi\""'
        p, _, _, t, _ = self.ok(s)
        self.assertEqual(t.lexeme, s)
        self.assertEqual(p, len(s))

    def test_escaped_single_quote(self):
        self.assertEqual(self.ok(r"'\''")[3].lexeme, r"'\''")

    def test_escaped_backslash_then_close(self):
        s = r'"a\\"'
        self.assertEqual(self.ok(s)[3].lexeme, s)

    def test_other_quote_inside_is_literal(self):
        self.assertEqual(self.ok('"it\'s"')[3].lexeme, '"it\'s"')

    def test_token_position_and_offset(self):
        src = 'x = "ab";'
        p, l, c, t, _ = self.ok(src, pos=4, line=3, col=5)
        self.assertEqual((t.line, t.column), (3, 5))
        self.assertEqual((p, l, c), (8, 3, 9))

    def test_stops_at_closing_quote(self):
        p, _, _, t, _ = self.ok('"ab" "cd"')
        self.assertEqual((t.lexeme, p), ('"ab"', 4))

    def test_unclosed_at_newline(self):
        src = '"abc\nnext'
        p, l, c, t, d = scan_string(src, 0, 1, 1)
        self.assertIsNone(t)
        self.assertEqual(d.code, ErrorCode.LEX_UNCLOSED_STRING)
        self.assertEqual((d.line, d.column), (1, 1))
        self.assertEqual(src[p], "\n")
        self.assertEqual(l, 1)

    def test_unclosed_at_eof(self):
        src = "'abc"
        p, l, c, t, d = scan_string(src, 0, 2, 7)
        self.assertIsNone(t)
        self.assertEqual(d.code, ErrorCode.LEX_UNCLOSED_STRING)
        self.assertEqual((d.line, d.column), (2, 7))
        self.assertEqual(p, len(src))

    def test_unclosed_reports_start_not_end(self):
        _, _, _, _, d = scan_string('x = "abc', 4, 1, 5)
        self.assertEqual((d.line, d.column), (1, 5))

    def test_lone_quote_at_eof(self):
        _, _, _, t, d = scan_string('"', 0, 1, 1)
        self.assertIsNone(t)
        self.assertEqual(d.code, ErrorCode.LEX_UNCLOSED_STRING)

    def test_dangling_backslash_at_eof(self):
        _, _, _, t, d = scan_string('"abc\\', 0, 1, 1)
        self.assertIsNone(t)
        self.assertIsNotNone(d)

    def test_mismatched_quote_is_unclosed(self):
        _, _, _, t, d = scan_string("\"abc'", 0, 1, 1)
        self.assertIsNone(t)
        self.assertIsNotNone(d)


class TestScanOperator(unittest.TestCase):
    def op(self, src, pos=0, line=1, col=1):
        return scan_operator(src, pos, line, col)

    def test_two_char_logops(self):
        for s in ("==", "!=", "<=", ">=", "&&", "||"):
            p, l, c, t = self.op(s)
            self.assertEqual((t.type, t.lexeme), (TokenType.LOGOP, s))
            self.assertEqual((p, c), (2, 3))

    def test_math_ops(self):
        for s in "+-*/%":
            p, l, c, t = self.op(s)
            self.assertEqual((t.type, t.lexeme), (TokenType.MATHOP, s))
            self.assertEqual((p, c), (1, 2))

    def test_assign(self):
        t = self.op("= 5")[3]
        self.assertEqual((t.type, t.lexeme), (TokenType.ASSIGN, "="))

    def test_single_logops(self):
        for s in "<>!":
            t = self.op(s + " ")[3]
            self.assertEqual((t.type, t.lexeme), (TokenType.LOGOP, s))

    def test_maximal_munch_ge(self):
        p, _, _, t = self.op(">=")
        self.assertEqual((t.lexeme, p), (">=", 2))

    def test_assign_vs_equals(self):
        self.assertEqual(self.op("==")[3].lexeme, "==")
        p, _, _, t = self.op("= =")
        self.assertEqual((t.type, p), (TokenType.ASSIGN, 1))

    def test_triple_equals_munches_two_then_one(self):
        p, _, c, t = self.op("===")
        self.assertEqual(t.lexeme, "==")
        p2, _, _, t2 = self.op("===", pos=p, col=c)
        self.assertEqual(t2.type, TokenType.ASSIGN)

    def test_not_equal_vs_not(self):
        self.assertEqual(self.op("!=")[3].lexeme, "!=")
        self.assertEqual(self.op("!x")[3].lexeme, "!")

    def test_lone_ampersand_and_pipe(self):
        for s in ("&", "&x", "|", "|x"):
            p, l, c, t = self.op(s)
            self.assertIsNone(t)
            self.assertEqual((p, c), (0, 1))

    def test_non_operator_char(self):
        self.assertIsNone(self.op("@")[3])
        self.assertIsNone(self.op("a")[3])

    def test_position_offsets(self):
        t = self.op("a >= b", pos=2, line=4, col=3)
        self.assertEqual((t[0], t[1], t[2]), (4, 4, 5))
        self.assertEqual((t[3].line, t[3].column), (4, 3))

    def test_operator_at_eof(self):
        self.assertIsNone(self.op("", 0)[3])
        self.assertEqual(self.op("a<", 1)[3].lexeme, "<")

    def test_slash_not_comment_handling(self):
        # Comment detection is the Lexer's job; '/' alone is MATHOP.
        self.assertEqual(self.op("/ 2")[3].type, TokenType.MATHOP)


if __name__ == "__main__":
    unittest.main()
