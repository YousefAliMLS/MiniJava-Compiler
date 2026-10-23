"""Focused unit tests for Member 4's identifier and number scanner."""
from __future__ import annotations

import unittest

from minijava.diagnostics import ErrorCode
from minijava.scanner_ident_num import scan_identifier_or_number
from minijava.symbol_table import IdentifierTable
from minijava.tokens import TokenType


class ScannerIdentifierNumberTests(unittest.TestCase):
    def scan(self, source: str, line: int = 1, col: int = 1):
        table = IdentifierTable()
        result = scan_identifier_or_number(source, 0, line, col, table)
        return result, table

    def test_standard_identifier(self):
        for name in ("age", "studentName", "total_marks", "_count", "A", "x9"):
            with self.subTest(name=name):
                (pos, line, col, token, diag), table = self.scan(name)
                self.assertEqual(pos, len(name))
                self.assertEqual((line, col), (1, len(name) + 1))
                self.assertEqual(token.type, TokenType.IDENTIFIER)
                self.assertEqual(token.lexeme, name)
                self.assertIsNone(diag)
                self.assertIn(name, table)

    def test_all_reserved_keywords(self):
        expected = {
            "class": TokenType.CLASS, "public": TokenType.PUBLIC,
            "static": TokenType.STATIC, "void": TokenType.VOID,
            "int": TokenType.INT, "float": TokenType.FLOAT,
            "boolean": TokenType.BOOLEAN_TYPE, "char": TokenType.CHAR,
            "String": TokenType.STRING_TYPE, "if": TokenType.IF,
            "else": TokenType.ELSE, "while": TokenType.WHILE,
            "for": TokenType.FOR, "return": TokenType.RETURN,
            "main": TokenType.MAIN, "true": TokenType.BOOLEAN,
            "false": TokenType.BOOLEAN,
        }
        for lexeme, token_type in expected.items():
            with self.subTest(lexeme=lexeme):
                (pos, _, col, token, diag), table = self.scan(lexeme)
                self.assertEqual(pos, len(lexeme))
                self.assertEqual(col, len(lexeme) + 1)
                self.assertEqual(token.type, token_type)
                self.assertIsNone(diag)
                self.assertEqual(len(table), 0)

    def test_case_sensitive_keyword(self):
        (pos, _, _, token, diag), table = self.scan("Class")
        self.assertEqual(pos, 5)
        self.assertEqual(token.type, TokenType.IDENTIFIER)
        self.assertIsNone(diag)
        self.assertIn("Class", table)

    def test_integer_numbers(self):
        for number in ("10", "0", "123456"):
            with self.subTest(number=number):
                (pos, _, col, token, diag), _ = self.scan(number)
                self.assertEqual(pos, len(number))
                self.assertEqual(col, len(number) + 1)
                self.assertEqual(token.type, TokenType.NUMBER)
                self.assertEqual(token.lexeme, number)
                self.assertIsNone(diag)

    def test_floating_point_numbers(self):
        for number in ("85.5", "0.0", "12.34", "1.23456"):
            with self.subTest(number=number):
                (pos, _, col, token, diag), _ = self.scan(number)
                self.assertEqual(pos, len(number))
                self.assertEqual(col, len(number) + 1)
                self.assertEqual(token.type, TokenType.NUMBER)
                self.assertEqual(token.lexeme, number)
                self.assertIsNone(diag)

    def test_decimal_point_without_following_digit_is_not_consumed(self):
        (pos, _, col, token, diag), _ = self.scan("10.")
        self.assertEqual((pos, col), (2, 3))
        self.assertEqual(token.lexeme, "10")
        self.assertIsNone(diag)

    def test_number_followed_by_delimiter(self):
        for source in ("10;", "20)", "7,", "42 "):
            with self.subTest(source=source):
                (pos, _, _, token, diag), _ = self.scan(source)
                self.assertEqual(token.type, TokenType.NUMBER)
                self.assertIsNone(diag)
                self.assertEqual(pos, len(source.rstrip(" ;),")) if source.rstrip(" ;),") else 0)

    def test_invalid_identifiers(self):
        for lexeme in ("1name", "2_count", "3abc", "25xyz", "8A", "0_name"):
            with self.subTest(lexeme=lexeme):
                (pos, line, col, token, diag), table = self.scan(lexeme)
                self.assertEqual(pos, len(lexeme))
                self.assertEqual((line, col), (1, len(lexeme) + 1))
                self.assertIsNone(token)
                self.assertEqual(diag.code, ErrorCode.LEX_INVALID_IDENTIFIER)
                self.assertEqual(diag.args["lexeme"], lexeme)
                self.assertEqual((diag.line, diag.column), (1, 1))
                self.assertEqual(len(table), 0)

    def test_invalid_identifier_diagnostic_format(self):
        (pos, _, _, token, diag), _ = self.scan("1name")
        self.assertEqual(diag.format(), "Error: invalid identifier '1name' at line 1, column 1.")
        self.assertIsNone(token)
        self.assertEqual(pos, 5)

    def test_invalid_identifier_with_nondefault_coordinates(self):
        table = IdentifierTable()
        _, _, _, token, diag = scan_identifier_or_number("xx 2_count", 3, 4, 7, table)
        self.assertIsNone(token)
        self.assertEqual((diag.line, diag.column), (4, 7))
        self.assertEqual(diag.args["lexeme"], "2_count")

    def test_identifier_occurrences_are_recorded(self):
        table = IdentifierTable()
        scan_identifier_or_number("student", 0, 2, 4, table)
        scan_identifier_or_number("student", 0, 3, 8, table)
        entry = table.lookup("student")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.occurrences, [(2, 4), (3, 8)])

    def test_keywords_are_not_recorded_as_identifiers(self):
        table = IdentifierTable()
        scan_identifier_or_number("class", 0, 1, 1, table)
        self.assertEqual(len(table), 0)

    def test_identifier_can_end_at_source_end(self):
        (pos, _, _, token, diag), _ = self.scan("endOfInput")
        self.assertEqual(pos, len("endOfInput"))
        self.assertEqual(token.lexeme, "endOfInput")
        self.assertIsNone(diag)

    def test_number_can_end_at_source_end(self):
        (pos, _, _, token, diag), _ = self.scan("987")
        self.assertEqual(pos, 3)
        self.assertEqual(token.type, TokenType.NUMBER)
        self.assertIsNone(diag)

    def test_empty_input_does_not_advance(self):
        table = IdentifierTable()
        result = scan_identifier_or_number("", 0, 1, 1, table)
        self.assertEqual(result, (0, 1, 1, None, None))

    def test_unsupported_start_does_not_advance(self):
        table = IdentifierTable()
        result = scan_identifier_or_number("+", 0, 1, 1, table)
        self.assertEqual(result, (0, 1, 1, None, None))

    def test_identifier_digits_and_underscores(self):
        name = "_a1_B2"
        (pos, _, _, token, diag), table = self.scan(name)
        self.assertEqual(pos, len(name))
        self.assertEqual(token.lexeme, name)
        self.assertIsNone(diag)
        self.assertIn(name, table)

    def test_float_followed_by_identifier_is_invalid(self):
        source = "12.34abc"
        (pos, _, _, token, diag), _ = self.scan(source)
        self.assertEqual(pos, len(source))
        self.assertIsNone(token)
        self.assertEqual(diag.code, ErrorCode.LEX_INVALID_IDENTIFIER)
        self.assertEqual(diag.args["lexeme"], source)

    def test_invalid_identifier_consumes_full_suffix(self):
        source = "1abc_23more"
        (pos, _, _, token, diag), _ = self.scan(source)
        self.assertEqual(pos, len(source))
        self.assertIsNone(token)
        self.assertEqual(diag.args["lexeme"], source)

    def test_identifier_coordinates_are_preserved(self):
        table = IdentifierTable()
        _, _, _, token, _ = scan_identifier_or_number("value", 0, 9, 12, table)
        self.assertEqual((token.line, token.column), (9, 12))
        self.assertEqual(table.lookup("value").occurrences, [(9, 12)])


if __name__ == "__main__":
    unittest.main()
