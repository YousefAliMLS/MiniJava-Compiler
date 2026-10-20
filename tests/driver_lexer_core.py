from __future__ import annotations

import unittest
from dataclasses import dataclass

from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic
from minijava.symbol_table import IdentifierTable
from minijava.tokens import DELIMITERS, TokenType, Token
from minijava.scanner_ident_num import scan_identifier_or_number
from minijava.scanner_str_op import scan_string, scan_operator


@dataclass
class LexResult:
    tokens: list[Token]
    diagnostics: list[Diagnostic]
    identifier_table: IdentifierTable


class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []
        self.identifier_table = IdentifierTable()

    def tokenize(self) -> LexResult:
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()

            if self.pos >= len(self.source):
                break

            c = self._peek()
            start_line = self.line
            start_col = self.column

            if c in DELIMITERS:
                self.tokens.append(
                    Token(
                        type=DELIMITERS[c],
                        lexeme=c,
                        line=start_line,
                        column=start_col,
                    )
                )
                self._advance()

            elif (
                ('a' <= c <= 'z')
                or ('A' <= c <= 'Z')
                or c == '_'
                or ('0' <= c <= '9')
            ):
                new_pos, new_line, new_col, tok, diag = scan_identifier_or_number(
                    self.source,
                    self.pos,
                    self.line,
                    self.column,
                    self.identifier_table,
                )
                self.pos, self.line, self.column = new_pos, new_line, new_col
                if tok:
                    self.tokens.append(tok)
                if diag:
                    self.diagnostics.append(diag)

            elif c in ('"', "'"):
                new_pos, new_line, new_col, tok, diag = scan_string(
                    self.source, self.pos, self.line, self.column
                )
                self.pos, self.line, self.column = new_pos, new_line, new_col
                if tok:
                    self.tokens.append(tok)
                if diag:
                    self.diagnostics.append(diag)

            elif c in ('=', '+', '-', '*', '/', '%', '<', '>', '!', '&', '|'):
                new_pos, new_line, new_col, tok = scan_operator(
                    self.source, self.pos, self.line, self.column
                )
                if tok:
                    self.pos, self.line, self.column = (
                        new_pos,
                        new_line,
                        new_col,
                    )
                    self.tokens.append(tok)
                else:
                    self.diagnostics.append(
                        make_diagnostic(
                            ErrorCode.LEX_INVALID_CHARACTER,
                            line=start_line,
                            column=start_col,
                            lexeme=c,
                        )
                    )
                    self._advance()

            else:
                self.diagnostics.append(
                    make_diagnostic(
                        ErrorCode.LEX_INVALID_CHARACTER,
                        line=start_line,
                        column=start_col,
                        lexeme=c,
                    )
                )
                self._advance()

        self.tokens.append(
            Token(
                type=TokenType.EOF,
                lexeme="",
                line=self.line,
                column=self.column,
            )
        )

        return LexResult(
            tokens=self.tokens,
            diagnostics=self.diagnostics,
            identifier_table=self.identifier_table,
        )

    def _peek(self, offset: int = 0) -> str | None:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self) -> str:
        c = self.source[self.pos]
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            c = self._peek()

            if c in (' ', '\t', '\n', '\r', '\f', '\v'):
                self._advance()

            elif c == '/' and self._peek(1) == '/':
                self._advance()
                self._advance()
                while self.pos < len(self.source) and self._peek() != '\n':
                    self._advance()

            elif c == '/' and self._peek(1) == '*':
                start_line = self.line
                start_col = self.column
                self._advance()
                self._advance()
                closed = False

                while self.pos < len(self.source):
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()

                if not closed:
                    self.diagnostics.append(
                        make_diagnostic(
                            ErrorCode.LEX_UNCLOSED_COMMENT,
                            line=start_line,
                            column=start_col,
                        )
                    )
                    break
            else:
                break


def tokenize(source: str) -> LexResult:
    return Lexer(source).tokenize()


class TestDriverLexerCore(unittest.TestCase):

    # --- 1. EOF emission tests ---
    def test_eof_empty_string(self):
        res = tokenize("")
        self.assertEqual(len(res.tokens), 1)
        self.assertEqual(res.tokens[0].type, TokenType.EOF)

    def test_eof_coordinates(self):
        res = tokenize("   \n  ")
        eof = res.tokens[0]
        self.assertEqual(eof.line, 2)
        self.assertEqual(eof.column, 3)

    # --- 2. Whitespace skipping tests ---
    def test_skip_spaces(self):
        res = tokenize("     ")
        self.assertEqual(len(res.tokens), 1)

    def test_skip_tabs(self):
        res = tokenize("\t\t")
        self.assertEqual(res.tokens[0].column, 3)

    def test_skip_newlines(self):
        res = tokenize("\n\n\n")
        self.assertEqual(res.tokens[0].line, 4)
        self.assertEqual(res.tokens[0].column, 1)

    def test_crlf_handling(self):
        res = tokenize("\r\n\r\n")
        self.assertEqual(res.tokens[0].line, 3)

    # --- 3. Single-line comment tests ---
    def test_single_line_comment_eof(self):
        res = tokenize("// This is a comment")
        self.assertEqual(len(res.tokens), 1)

    def test_single_line_comment_newline(self):
        res = tokenize("// comment\n;")
        self.assertEqual(len(res.tokens), 2)
        self.assertEqual(res.tokens[0].type, TokenType.SEMICOLON)
        self.assertEqual(res.tokens[0].line, 2)

    def test_multiple_single_line_comments(self):
        res = tokenize("// one\n// two\n// three")
        self.assertEqual(len(res.tokens), 1)

    # --- 4. Multi-line comment tests ---
    def test_multi_line_comment_single_line(self):
        res = tokenize("/* comment */ ;")
        self.assertEqual(res.tokens[0].type, TokenType.SEMICOLON)

    def test_multi_line_comment_multiple_lines(self):
        res = tokenize("/* \n * comment \n */ ;")
        self.assertEqual(res.tokens[0].line, 3)

    def test_nested_delimiters_in_comments_ignored(self):
        res = tokenize("/* { ; } */")
        self.assertEqual(len(res.tokens), 1)

    def test_unclosed_multi_line_comment(self):
        res = tokenize("/* unclosed")
        self.assertEqual(len(res.diagnostics), 1)
        self.assertEqual(res.diagnostics[0].code, ErrorCode.LEX_UNCLOSED_COMMENT)
        self.assertEqual(res.diagnostics[0].line, 1)
        self.assertEqual(res.diagnostics[0].column, 1)

    def test_unclosed_multi_line_comment_advanced_position(self):
        res = tokenize("  \n  /* unclosed\n\n")
        self.assertEqual(res.diagnostics[0].line, 2)
        self.assertEqual(res.diagnostics[0].column, 3)

    # --- 5. Delimiter tests ---
    def test_lpar(self):
        self.assertEqual(tokenize("(").tokens[0].type, TokenType.LPAR)

    def test_rpar(self):
        self.assertEqual(tokenize(")").tokens[0].type, TokenType.RPAR)

    def test_lcur(self):
        self.assertEqual(tokenize("{").tokens[0].type, TokenType.LCUR)

    def test_rcur(self):
        self.assertEqual(tokenize("}").tokens[0].type, TokenType.RCUR)

    def test_lsqu(self):
        self.assertEqual(tokenize("[").tokens[0].type, TokenType.LSQU)

    def test_rsqu(self):
        self.assertEqual(tokenize("]").tokens[0].type, TokenType.RSQU)

    def test_semicolon(self):
        self.assertEqual(tokenize(";").tokens[0].type, TokenType.SEMICOLON)

    def test_comma(self):
        self.assertEqual(tokenize(",").tokens[0].type, TokenType.COMMA)

    def test_dot(self):
        self.assertEqual(tokenize(".").tokens[0].type, TokenType.DOT)

    def test_all_delimiters(self):
        res = tokenize("(){}[];,.")
        types = [t.type for t in res.tokens[:-1]]
        expected = [
            TokenType.LPAR,
            TokenType.RPAR,
            TokenType.LCUR,
            TokenType.RCUR,
            TokenType.LSQU,
            TokenType.RSQU,
            TokenType.SEMICOLON,
            TokenType.COMMA,
            TokenType.DOT,
        ]
        self.assertEqual(types, expected)

    # --- 6. Invalid Character tests ---
    def test_invalid_character_at(self):
        res = tokenize("@")
        self.assertEqual(len(res.diagnostics), 1)
        self.assertEqual(res.diagnostics[0].code, ErrorCode.LEX_INVALID_CHARACTER)
        self.assertEqual(res.diagnostics[0].args["lexeme"], "@")

    def test_invalid_character_hash(self):
        res = tokenize("  #  ")
        self.assertEqual(res.diagnostics[0].line, 1)
        self.assertEqual(res.diagnostics[0].column, 3)
        self.assertEqual(res.diagnostics[0].args["lexeme"], "#")


if __name__ == "__main__":
    unittest.main()