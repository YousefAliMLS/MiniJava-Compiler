from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from minijava.diagnostics import Phase
from minijava.driver import (
    CompilationResult,
    compile_source,
    format_report,
    main,
    read_source,
)
from minijava.lexer import tokenize
from minijava.tokens import TokenType


class TestDriver(unittest.TestCase):

    def setUp(self) -> None:
        self.tmp_dir = Path("tests/temp_sandbox")
        self.tmp_dir.mkdir(exist_ok=True)

    def tearDown(self) -> None:
        for p in self.tmp_dir.glob("*"):
            p.unlink()
        if self.tmp_dir.exists():
            self.tmp_dir.rmdir()

    def test_read_source_success(self):
        sample_file = self.tmp_dir / "valid.mj"
        sample_file.write_text("class Main {}", encoding="utf-8")
        content = read_source(str(sample_file))
        self.assertEqual(content, "class Main {}")

    def test_read_source_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            read_source(str(self.tmp_dir / "nonexistent.mj"))

    def test_compile_source_clean(self):
        source = "class Main { public static void main(String[] args) {} }"
        result = compile_source(source, phase=Phase.LEXICAL)
        self.assertTrue(result.success)
        self.assertEqual(len(result.lex.diagnostics), 0)

    def test_compile_source_with_error(self):
        source = "int x = 10 @ 5;"
        result = compile_source(source, phase=Phase.LEXICAL)
        self.assertFalse(result.success)
        self.assertEqual(len(result.lex.diagnostics), 1)

    def test_format_report_clean(self):
        source = "class Test {}"
        lex_res = tokenize(source)
        comp_res = CompilationResult(
            source_path="test.mj",
            phase=Phase.LEXICAL,
            lex=lex_res,
            success=True,
        )
        report = format_report(comp_res)
        self.assertIn("=== Tokens ===", report)
        self.assertIn("=== Symbol Table ===", report)
        self.assertIn("=== Errors ===\n(none)", report)
        self.assertIn("Lexical analysis completed successfully with no errors.", report)

    def test_format_report_with_errors(self):
        source = "int x = @;"
        lex_res = tokenize(source)
        comp_res = CompilationResult(
            source_path="test.mj",
            phase=Phase.LEXICAL,
            lex=lex_res,
            success=False,
        )
        report = format_report(comp_res)
        self.assertIn("=== Errors ===", report)
        self.assertIn("invalid character '@'", report)
        self.assertIn("Lexical analysis failed with 1 error(s).", report)

    @patch("sys.argv", ["python3 -m minijava", "nonexistent_file.mj"])
    def test_main_cli_io_error_returns_exit_code_2(self):
        exit_code = main()
        self.assertEqual(exit_code, 2)

    @patch("sys.argv", ["python3 -m minijava", ""])
    def test_main_cli_success_returns_exit_code_0(self):
        sample_file = self.tmp_dir / "sample.mj"
        sample_file.write_text("class Main {}", encoding="utf-8")
        with patch("sys.argv", ["python3 -m minijava", str(sample_file)]):
            exit_code = main()
            self.assertEqual(exit_code, 0)

    @patch("sys.argv", ["python3 -m minijava", ""])
    def test_main_cli_lex_error_returns_exit_code_1(self):
        sample_file = self.tmp_dir / "error.mj"
        sample_file.write_text("int x = @;", encoding="utf-8")
        with patch("sys.argv", ["python3 -m minijava", str(sample_file)]):
            exit_code = main()
            self.assertEqual(exit_code, 1)


if __name__ == "__main__":
    unittest.main()