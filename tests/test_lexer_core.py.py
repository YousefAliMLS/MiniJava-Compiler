import unittest
from unittest.mock import patch
from minijava.lexer import Lexer, tokenize
from minijava.tokens import Token, TokenType
from minijava.diagnostics import ErrorCode

class TestLexerCore(unittest.TestCase):

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
        expected = [TokenType.LPAR, TokenType.RPAR, TokenType.LCUR, TokenType.RCUR, 
                    TokenType.LSQU, TokenType.RSQU, TokenType.SEMICOLON, 
                    TokenType.COMMA, TokenType.DOT]
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