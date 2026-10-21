from __future__ import annotations

from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic
from minijava.symbol_table import IdentifierTable
from minijava.tokens import KEYWORDS, Token, TokenType


def scan_identifier_or_number(
    source: str,
    pos: int,
    line: int,
    col: int,
    id_table: IdentifierTable,
) -> tuple[int, int, int, Token | None, Diagnostic | None]:
    """Scans an identifier, keyword, valid number, or invalid identifier."""
    start_pos = pos
    start_line = line
    start_col = col
    c = source[pos]

    # Check for invalid identifier starting with a digit (e.g., "1name")
    if "0" <= c <= "9":
        lexeme_chars = []
        curr_pos = pos
        curr_col = col
        while curr_pos < len(source):
            ch = source[curr_pos]
            if (
                ("a" <= ch <= "z")
                or ("A" <= ch <= "Z")
                or ("0" <= ch <= "9")
                or ch == "_"
            ):
                lexeme_chars.append(ch)
                curr_pos += 1
                curr_col += 1
            else:
                break
        lexeme = "".join(lexeme_chars)

        # If it contains letters/underscores right after digits, it's an invalid identifier
        has_letters = any(
            ("a" <= ch <= "z") or ("A" <= ch <= "Z") or ch == "_"
            for ch in lexeme
        )
        if has_letters:
            diag = make_diagnostic(
                ErrorCode.LEX_INVALID_IDENTIFIER,
                line=start_line,
                column=start_col,
                lexeme=lexeme,
            )
            return curr_pos, start_line, curr_col, None, diag

        # Otherwise, scan as a valid number (integer or float)
        is_float = False
        while curr_pos < len(source):
            ch = source[curr_pos]
            if "0" <= ch <= "9":
                curr_pos += 1
                curr_col += 1
            elif ch == "." and not is_float:
                # Check if next char is a digit
                if curr_pos + 1 < len(source) and "0" <= source[curr_pos + 1] <= "9":
                    is_float = True
                    curr_pos += 1
                    curr_col += 1
                else:
                    break
            else:
                break
        number_lexeme = source[start_pos:curr_pos]
        token = Token(
            type=TokenType.NUMBER,
            lexeme=number_lexeme,
            line=start_line,
            column=start_col,
        )
        return curr_pos, start_line, curr_col, token, None

    # Scan identifier or keyword starting with letter or underscore
    if ("a" <= c <= "z") or ("A" <= c <= "Z") or c == "_":
        lexeme_chars = []
        curr_pos = pos
        curr_col = col
        while curr_pos < len(source):
            ch = source[curr_pos]
            if (
                ("a" <= ch <= "z")
                or ("A" <= ch <= "Z")
                or ("0" <= ch <= "9")
                or ch == "_"
            ):
                lexeme_chars.append(ch)
                curr_pos += 1
                curr_col += 1
            else:
                break
        lexeme = "".join(lexeme_chars)

        # Check keyword table
        if lexeme in KEYWORDS:
            tok_type = KEYWORDS[lexeme]
            token = Token(
                type=tok_type,
                lexeme=lexeme,
                line=start_line,
                column=start_col,
            )
        else:
            token = Token(
                type=TokenType.IDENTIFIER,
                lexeme=lexeme,
                line=start_line,
                column=start_col,
            )
            id_table.add_occurrence(lexeme, start_line, start_col)

        return curr_pos, start_line, curr_col, token, None

    return pos, line, col, None, None