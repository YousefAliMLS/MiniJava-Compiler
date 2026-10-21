from __future__ import annotations
import unittest
from dataclasses import is_dataclass

from minijava.tokens import TokenType, Token, KEYWORDS, MATH_OPERATORS, LOGICAL_OPERATORS, DELIMITERS
from minijava.diagnostics import Phase, ErrorCode, Diagnostic, make_diagnostic
from minijava.symbol_table import IdentifierTable, IdentifierEntry


class TestContract(unittest.TestCase):

    def test_token_type_enum(self):
        self.assertIsInstance(TokenType.CLASS, TokenType)
        self.assertEqual(TokenType.CLASS.value, "CLASS")
        self.assertEqual(TokenType.EOF.value, "EOF")

    def test_token_dataclass(self):
        self.assertTrue(is_dataclass(Token))
        tok = Token(TokenType.IDENTIFIER, "x", 1, 1)
        self.assertEqual(tok.format(), "Lexeme: x, Token: IDENTIFIER")
        self.assertEqual(tok.describe(), "'x'")
        eof_tok = Token(TokenType.EOF, "", 1, 5)
        self.assertEqual(eof_tok.describe(), "end of input")

    def test_keywords_and_operators(self):
        self.assertIn("class", KEYWORDS)
        self.assertIn("String", KEYWORDS)
        self.assertIn("+", MATH_OPERATORS)
        self.assertIn("==", LOGICAL_OPERATORS)
        self.assertIn("(", DELIMITERS)

    def test_diagnostics_contract(self):
        self.assertTrue(is_dataclass(Diagnostic))
        diag = make_diagnostic(ErrorCode.LEX_INVALID_CHARACTER, 1, 10, lexeme="@")
        self.assertEqual(diag.phase, Phase.LEXICAL)
        self.assertIn("invalid character '@'", diag.message())
        self.assertIn("Error:", diag.format())

    def test_symbol_table_contract(self):
        table = IdentifierTable()
        entry = table.add_occurrence("count", 1, 5)
        self.assertEqual(entry.index, 1)
        self.assertEqual(entry.name, "count")
        self.assertIn("count", table)


if __name__ == "__main__":
    unittest.main()