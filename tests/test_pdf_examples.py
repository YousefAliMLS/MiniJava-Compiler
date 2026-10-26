"""Acceptance tests for the four error examples specified in the project docs.

The exact 41-token sample assertion is intentionally isolated below because the
uploaded planning files refer to the official course PDF but do not include its
13-line sample source or complete expected token listing. Add that golden case
once the official PDF/sample is available in the project workspace.
"""
from __future__ import annotations

import unittest

from minijava.diagnostics import ErrorCode
from minijava.lexer import tokenize


class PdfAcceptanceTests(unittest.TestCase):
    def diagnostic_for(self, source: str, code: ErrorCode):
        result = tokenize(source)
        matches = [diagnostic for diagnostic in result.diagnostics if diagnostic.code is code]
        self.assertTrue(matches, f"Expected {code.name} for source: {source!r}")
        return matches[0], result

    def test_pdf_invalid_character_example(self):
        diagnostic, _ = self.diagnostic_for("int x = 10 @ 5;", ErrorCode.LEX_INVALID_CHARACTER)
        self.assertEqual(
            diagnostic.format(),
            "Error: invalid character '@' at line 1, column 12.",
        )

    def test_pdf_invalid_identifier_example(self):
        diagnostic, result = self.diagnostic_for("1name = 5;", ErrorCode.LEX_INVALID_IDENTIFIER)
        self.assertEqual(
            diagnostic.format(),
            "Error: invalid identifier '1name' at line 1, column 1.",
        )
        self.assertFalse(any(token.lexeme == "1name" for token in result.tokens))

    def test_pdf_unclosed_string_example(self):
        diagnostic, _ = self.diagnostic_for('String name = "Ali;', ErrorCode.LEX_UNCLOSED_STRING)
        self.assertEqual(
            diagnostic.format(),
            "Error: unclosed string literal starting at line 1, column 15.",
        )

    def test_pdf_unclosed_comment_example(self):
        diagnostic, _ = self.diagnostic_for(
            "/* This comment does not end", ErrorCode.LEX_UNCLOSED_COMMENT
        )
        self.assertEqual(
            diagnostic.format(),
            "Error: unclosed comment starting at line 1, column 1.",
        )

    def test_pdf_sample_program_has_exact_41_tokens(self):
        source = """class Student {
    public static void main() {
        int age = 20;
        float grade = 85.5;
        String name = "Ali";
        if (grade >= 50) {
            grade = grade + 5;
        }
    }
}"""
        from minijava.tokens import TokenType
        result = tokenize(source)
        tokens_no_eof = [t for t in result.tokens if t.type is not TokenType.EOF]
        self.assertEqual(len(tokens_no_eof), 41)
        self.assertEqual(tokens_no_eof[0].type, TokenType.CLASS)
        self.assertEqual(tokens_no_eof[1].lexeme, "Student")
        self.assertEqual(tokens_no_eof[18].lexeme, "85.5")
        self.assertEqual(tokens_no_eof[18].type, TokenType.NUMBER)
        self.assertEqual(tokens_no_eof[23].lexeme, '"Ali"')
        self.assertEqual(tokens_no_eof[23].type, TokenType.STRING)
        self.assertEqual(len(result.diagnostics), 0)


if __name__ == "__main__":
    unittest.main()
