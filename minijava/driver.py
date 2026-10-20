from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path

from minijava.diagnostics import Diagnostic, Phase
from minijava.lexer import tokenize, LexResult
from minijava.symbol_table import IdentifierTable, format_identifier_table
from minijava.tokens import TokenType


@dataclass
class CompilationResult:
    source_path: str
    phase: Phase
    lex: LexResult
    success: bool


def read_source(path: str) -> str:
    """Reads source file with UTF-8-BOM normalization and universal newlines."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Source file not found: {path}")
    return file_path.read_text(encoding="utf-8-sig")


def compile_source(source: str, phase: Phase = Phase.LEXICAL) -> CompilationResult:
    """Coordinates Phase 1 lexical analysis execution."""
    lex_result = tokenize(source)
    success = len(lex_result.diagnostics) == 0
    return CompilationResult(
        source_path="<input>",
        phase=phase,
        lex=lex_result,
        success=success,
    )


def format_report(
    result: CompilationResult,
    show_tokens: bool = False,
    show_symbols: bool = False,
) -> str:
    """Formats standard compiler output report with headers:
    === Tokens ===, === Symbol Table ===, === Errors ===, === Result ===.
    """
    sections: list[str] = []

    # 1. Tokens Section
    if result.phase == Phase.LEXICAL or show_tokens:
        token_lines = [
            t.format()
            for t in result.lex.tokens
            if t.type is not TokenType.EOF
        ]
        tokens_body = "\n".join(token_lines) if token_lines else "(none)"
        sections.append(f"=== Tokens ===\n{tokens_body}")

    # 2. Symbol Table Section
    if result.phase == Phase.LEXICAL or show_symbols:
        symbols_body = format_identifier_table(result.lex.identifier_table)
        sections.append(f"=== Symbol Table ===\n{symbols_body}")

    # 3. Errors Section
    error_lines = [d.format() for d in result.lex.diagnostics]
    errors_body = "\n".join(error_lines) if error_lines else "(none)"
    sections.append(f"=== Errors ===\n{errors_body}")

    # 4. Result Section
    if result.success:
        result_body = "Lexical analysis completed successfully with no errors."
    else:
        err_count = len(result.lex.diagnostics)
        result_body = f"Lexical analysis failed with {err_count} error(s)."
    sections.append(f"=== Result ===\n{result_body}")

    return "\n\n".join(sections)


def main(argv: list[str] | None = None) -> int:
    """CLI driver entry point. Returns exit code:
    0: Clean compilation
    1: Lexical errors detected
    2: CLI usage error or I/O failure
    """
    parser = argparse.ArgumentParser(
        description="Mini Java Compiler - Phase 1 Lexical Analyzer",
        prog="python3 -m minijava",
    )
    parser.add_argument(
        "source",
        help="Path to the Mini Java source file (.mj or text)",
    )
    parser.add_argument(
        "--phase",
        type=str,
        default="lex",
        choices=["lex", "parse", "semantic"],
        help="Compilation phase to execute (default: lex)",
    )
    parser.add_argument(
        "--tokens",
        action="store_true",
        help="Explicitly force display of the token stream",
    )
    parser.add_argument(
        "--symbols",
        action="store_true",
        help="Explicitly force display of the identifier symbol table",
    )

    args = parser.parse_args(argv)

    # Map phase string to Phase enum
    phase_map = {
        "lex": Phase.LEXICAL,
        "parse": Phase.SYNTAX,
        "semantic": Phase.SEMANTIC,
    }
    phase = phase_map.get(args.phase, Phase.LEXICAL)

    try:
        source_code = read_source(args.source)
    except (FileNotFoundError, IOError, PermissionError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2

    comp_result = compile_source(source_code, phase=phase)
    comp_result.source_path = args.source

    report = format_report(
        comp_result,
        show_tokens=args.tokens,
        show_symbols=args.symbols,
    )
    print(report)

    # Return exit code: 0 if clean, 1 if lexical errors found
    return 0 if comp_result.success else 1


if __name__ == "__main__":
    sys.exit(main())