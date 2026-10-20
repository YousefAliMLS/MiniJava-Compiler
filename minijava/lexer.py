from __future__ import annotations
from dataclasses import dataclass
from minijava.tokens import Token, TokenType, DELIMITERS
from minijava.diagnostics import Diagnostic, ErrorCode, make_diagnostic
from minijava.symbol_table import IdentifierTable
from minijava.scanner_ident_num import scan_identifier_or_number
from minijava.scanner_str_op import scan_string, scan_operator

@dataclass
class LexResult:
    tokens: list[Token]
    diagnostics: list[Diagnostic]
    identifier_table: IdentifierTable

class Lexer:
    def __init__(self, source: str) -> None:
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: list[Token] = []
        self.diagnostics: list[Diagnostic] = []
        self.identifier_table = IdentifierTable()

    def tokenize(self) -> LexResult:
        while self.pos < len(self.source):
            self._skip_whitespace_and_comments()
            
            if self.pos >= len(self.source):
                break
                
            c = self._peek()
            start_line = self.line
            start_col = self.column

            if c in DELIMITERS:
                self.tokens.append(Token(
                    type=DELIMITERS[c],
                    lexeme=c,
                    line=start_line,
                    column=start_col
                ))
                self._advance()
                
            elif ('a' <= c <= 'z') or ('A' <= c <= 'Z') or c == '_' or ('0' <= c <= '9'):
                new_pos, new_line, new_col, tok, diag = scan_identifier_or_number(
                    self.source, self.pos, self.line, self.column, self.identifier_table
                )
                self.pos, self.line, self.column = new_pos, new_line, new_col
                if tok: self.tokens.append(tok)
                if diag: self.diagnostics.append(diag)
                
            elif c in ('"', "'"):
                new_pos, new_line, new_col, tok, diag = scan_string(
                    self.source, self.pos, self.line, self.column
                )
                self.pos, self.line, self.column = new_pos, new_line, new_col
                if tok: self.tokens.append(tok)
                if diag: self.diagnostics.append(diag)
                
            elif c in ('=', '+', '-', '*', '/', '%', '<', '>', '!', '&', '|'):
                new_pos, new_line, new_col, tok = scan_operator(
                    self.source, self.pos, self.line, self.column
                )
                if tok:
                    self.pos, self.line, self.column = new_pos, new_line, new_col
                    self.tokens.append(tok)
                else:
                    self.diagnostics.append(make_diagnostic(
                        ErrorCode.LEX_INVALID_CHARACTER,
                        line=start_line,
                        column=start_col,
                        lexeme=c
                    ))
                    self._advance()
                
            else:
                self.diagnostics.append(make_diagnostic(
                    ErrorCode.LEX_INVALID_CHARACTER, 
                    line=start_line, 
                    column=start_col, 
                    lexeme=c
                ))
                self._advance()

        self.tokens.append(Token(
            type=TokenType.EOF, 
            lexeme="", 
            line=self.line, 
            column=self.column
        ))
        
        return LexResult(
            tokens=self.tokens,
            diagnostics=self.diagnostics,
            identifier_table=self.identifier_table
        )

    def _peek(self, offset: int = 0) -> str | None:
        idx = self.pos + offset
        if idx < len(self.source):
            return self.source[idx]
        return None

    def _advance(self) -> str:
        c = self.source[self.pos]
        self.pos += 1
        if c == '\n':
            self.line += 1
            self.column = 1
        else:
            self.column += 1
        return c

    def _skip_whitespace_and_comments(self) -> None:
        while self.pos < len(self.source):
            c = self._peek()
            
            if c in (' ', '\t', '\n', '\r', '\f', '\v'):
                self._advance()
                
            elif c == '/' and self._peek(1) == '/':
                self._advance()
                self._advance()
                while self.pos < len(self.source) and self._peek() != '\n':
                    self._advance()
                    
            elif c == '/' and self._peek(1) == '*':
                start_line = self.line
                start_col = self.column
                self._advance()
                self._advance()
                closed = False
                
                while self.pos < len(self.source):
                    if self._peek() == '*' and self._peek(1) == '/':
                        self._advance()
                        self._advance()
                        closed = True
                        break
                    self._advance()
                    
                if not closed:
                    self.diagnostics.append(make_diagnostic(
                        ErrorCode.LEX_UNCLOSED_COMMENT, 
                        line=start_line, 
                        column=start_col
                    ))
                    break
            else:
                break

def tokenize(source: str) -> LexResult:
    return Lexer(source).tokenize()