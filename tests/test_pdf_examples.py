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

    @unittest.skip(
        "The uploaded planning files do not contain the official 13-line source and 41-token oracle. "
        "Enable this acceptance case after copying the exact sample from ProjectGuidelinesAndDetails.pdf."
    )
    def test_pdf_sample_program_has_exact_41_tokens(self):
        self.fail("Insert the official PDF sample and its 41 exact token expectations here.")


if __name__ == "__main__":
    unittest.main()
