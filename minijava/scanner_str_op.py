"""String-literal and operator scanning for the Mini Java lexer (Member 5).

No regular expressions are used (course rule REQ-05).
Columns are advanced one per character; the caller decides the base (0/1).
"""
from __future__ import annotations

from minijava.tokens import (
    Token, TokenType, MATH_OPERATORS, LOGICAL_OPERATORS,
    TWO_CHAR_OPERATORS, ASSIGN_OPERATOR
)
from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic

_QUOTES = ('"', "'")
_SINGLE_LOGOPS = ("<", ">", "!")


def scan_string(
    source: str,
    pos: int,
    line: int,
    col: int
) -> tuple[int, int, int, Token | None, Diagnostic | None]:
    """Scans a quoted string literal or reports an unclosed string error.

    Returns:
        (new_pos, new_line, new_col, token_or_none, diagnostic_or_none)
    """
    n = len(source)
    if pos >= n or source[pos] not in _QUOTES:
        return pos, line, col, None, None

    quote_char = source[pos]
    start_pos, start_line, start_col = pos, line, col
    i = pos + 1
    c = col + 1

    while i < n:
        ch = source[i]
        if ch == "\n":
            break
        if ch == "\\":
            # Escape: backslash + the escaped char are both part of the lexeme.
            if i + 1 >= n or source[i + 1] == "\n":
                # Dangling backslash at EOF / end of line: string is unclosed.
                i += 1
                c += 1
                break
            i += 2
            c += 2
            continue
        if ch == quote_char:
            i += 1
            c += 1
            lexeme = source[start_pos:i]
            tok = Token(TokenType.STRING, lexeme, start_line, start_col)
            return i, line, c, tok, None
        i += 1
        c += 1

    # Newline or EOF before the closing quote: resume at the newline / stop at EOF.
    diag = make_diagnostic(ErrorCode.LEX_UNCLOSED_STRING,
                           line=start_line, column=start_col)
    return i, line, c, None, diag


def scan_operator(
    source: str,
    pos: int,
    line: int,
    col: int
) -> tuple[int, int, int, Token | None]:
    """Scans operators using maximal munch.

    Returns:
        (new_pos, new_line, new_col, token_or_none)
    On token_or_none == None the position is NOT advanced, so the Lexer can
    report LEX_INVALID_CHARACTER for the offending character itself.
    """
    if pos >= len(source):
        return pos, line, col, None

    two = source[pos:pos + 2]
    if len(two) == 2 and two in TWO_CHAR_OPERATORS:
        return pos + 2, line, col + 2, Token(TokenType.LOGOP, two, line, col)

    c = source[pos]
    if c == ASSIGN_OPERATOR:
        tok = Token(TokenType.ASSIGN, c, line, col)
    elif c in MATH_OPERATORS:
        tok = Token(TokenType.MATHOP, c, line, col)
    elif c in _SINGLE_LOGOPS:
        tok = Token(TokenType.LOGOP, c, line, col)
    else:
        # Lone '&' / '|' or any non-operator character.
        return pos, line, col, None
    return pos + 1, line, col + 1, tok
