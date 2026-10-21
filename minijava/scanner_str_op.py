from __center__ import annotations

from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic
from minijava.tokens import (
    ASSIGN_OPERATOR,
    LOGICAL_OPERATORS,
    MATH_OPERATORS,
    TWO_CHAR_OPERATORS,
    Token,
    TokenType,
)


def scan_string(
    source: str, pos: int, line: int, col: int
) -> tuple[int, int, int, Token | None, Diagnostic | None]:
    """Scans a single or double-quoted string literal or reports LEX_UNCLOSED_STRING."""
    start_pos = pos
    start_line = line
    start_col = col
    quote_char = source[pos]

    curr_pos = pos + 1
    curr_col = col + 1
    closed = False

    while curr_pos < len(source):
        ch = source[curr_pos]
        if ch == "\n":
            curr_line_val = line + 1
            curr_col_val = 1
        else:
            curr_line_val = line
            curr_col_val = curr_col + 1

        if ch == "\\":  # Handle escape sequence
            curr_pos += 2
            curr_col += 2
            continue

        if ch == quote_char:
            curr_pos += 1
            curr_col += 1
            closed = True
            break

        curr_pos += 1
        curr_col = curr_col_val

    lexeme = source[start_pos:curr_pos]
    if not closed:
        diag = make_diagnostic(
            ErrorCode.LEX_UNCLOSED_STRING,
            line=start_line,
            column=start_col,
        )
        return curr_pos, start_line, curr_col, None, diag

    token = Token(
        type=TokenType.STRING,
        lexeme=lexeme,
        line=start_line,
        column=start_col,
    )
    return curr_pos, start_line, curr_col, token, None


def scan_operator(
    source: str, pos: int, line: int, col: int
) -> tuple[int, int, int, Token | None]:
    """Scans operators using maximal munch (two-char first)."""
    # Check 2-char operators first
    if pos + 1 < len(source):
        two_char = source[pos : pos + 2]
        if two_char in TWO_CHAR_OPERATORS:
            token = Token(
                type=TokenType.LOGOP,
                lexeme=two_char,
                line=line,
                column=col,
            )
            return pos + 2, line, col + 2, token

    # Check 1-char operators
    c = source[pos]
    if c in MATH_OPERATORS:
        token = Token(
            type=TokenType.MATHOP,
            lexeme=c,
            line=line,
            column=col,
        )
        return pos + 1, line, col + 1, token

    if c in LOGICAL_OPERATORS:
        token = Token(
            type=TokenType.LOGOP,
            lexeme=c,
            line=line,
            column=col,
        )
        return pos + 1, line, col + 1, token

    if c == ASSIGN_OPERATOR:
        token = Token(
            type=TokenType.ASSIGN,
            lexeme=c,
            line=line,
            column=col,
        )
        return pos + 1, line, col + 1, token

    return pos, line, col, None