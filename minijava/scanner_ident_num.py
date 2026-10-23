"""Hand-crafted scanner for Mini Java identifiers, keywords, and numeric literals.

This module is owned by Member 4. It intentionally uses character-by-character
scanning and does not use regular expressions or tokenization shortcuts.
"""
from __future__ import annotations

from minijava.tokens import Token, TokenType, KEYWORDS
from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic
from minijava.symbol_table import IdentifierTable


def _is_ascii_letter(char: str) -> bool:
    """Return whether char is an ASCII English letter."""
    return "a" <= char <= "z" or "A" <= char <= "Z"


def _is_digit(char: str) -> bool:
    """Return whether char is an ASCII decimal digit."""
    return "0" <= char <= "9"


def _is_identifier_part(char: str) -> bool:
    """Return whether char may occur after the first identifier character."""
    return _is_ascii_letter(char) or _is_digit(char) or char == "_"


def scan_identifier_or_number(
    source: str,
    pos: int,
    line: int,
    col: int,
    id_table: IdentifierTable,
) -> tuple[int, int, int, Token | None, Diagnostic | None]:
    """Scan an identifier, keyword, valid number, or invalid digit-prefixed name.

    Args:
        source: Complete source text being scanned.
        pos: Zero-based index of the first character to scan.
        line: One-based source line of that character.
        col: One-based source column of that character.
        id_table: Shared table in which non-keyword identifiers are recorded.

    Returns:
        ``(new_pos, new_line, new_col, token, diagnostic)``. Exactly one of
        ``token`` and ``diagnostic`` is present for a recognized lexeme; neither
        is present only when called at end of input or on an unsupported start.
        This helper consumes no newline, so the line is unchanged and the
        column advances by the number of consumed characters.
    """
    if pos < 0 or pos >= len(source):
        return pos, line, col, None, None

    start = pos
    first = source[pos]

    if _is_ascii_letter(first) or first == "_":
        pos += 1
        while pos < len(source) and _is_identifier_part(source[pos]):
            pos += 1
        lexeme = source[start:pos]
        token_type = KEYWORDS.get(lexeme)
        if token_type is None:
            token_type = TokenType.IDENTIFIER
            id_table.add_occurrence(lexeme, line, col)
        token = Token(type=token_type, lexeme=lexeme, line=line, column=col)
        return pos, line, col + (pos - start), token, None

    if _is_digit(first):
        # First consume the integer portion.
        pos += 1
        while pos < len(source) and _is_digit(source[pos]):
            pos += 1

        # A decimal point belongs to a float only when followed by a digit.
        if (
            pos + 1 < len(source)
            and source[pos] == "."
            and _is_digit(source[pos + 1])
        ):
            pos += 1
            while pos < len(source) and _is_digit(source[pos]):
                pos += 1

        # Digit-prefixed identifiers are one invalid lexeme, not NUMBER + ID.
        if pos < len(source) and (_is_ascii_letter(source[pos]) or source[pos] == "_"):
            pos += 1
            while pos < len(source) and _is_identifier_part(source[pos]):
                pos += 1
            invalid_lexeme = source[start:pos]
            diagnostic = make_diagnostic(
                ErrorCode.LEX_INVALID_IDENTIFIER,
                line=line,
                column=col,
                lexeme=invalid_lexeme,
            )
            return pos, line, col + (pos - start), None, diagnostic

        lexeme = source[start:pos]
        token = Token(type=TokenType.NUMBER, lexeme=lexeme, line=line, column=col)
        return pos, line, col + (pos - start), token, None

    # The central lexer decides what to do with punctuation/operators/etc.
    return pos, line, col, None, None
