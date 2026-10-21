from __future__ import annotations
from dataclasses import dataclass
from enum import Enum

class TokenType(Enum):
    CLASS = "CLASS"
    PUBLIC = "PUBLIC"
    STATIC = "STATIC"
    VOID = "VOID"
    INT = "INT"
    FLOAT = "FLOAT"
    BOOLEAN_TYPE = "BOOLEAN_TYPE"
    CHAR = "CHAR"
    STRING_TYPE = "STRING_TYPE"
    IF = "IF"
    ELSE = "ELSE"
    WHILE = "WHILE"
    FOR = "FOR"
    RETURN = "RETURN"
    MAIN = "MAIN"
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING = "STRING"
    BOOLEAN = "BOOLEAN"
    MATHOP = "MATHOP"
    LOGOP = "LOGOP"
    ASSIGN = "ASSIGN"
    LPAR = "LPAR"
    RPAR = "RPAR"
    LCUR = "LCUR"
    RCUR = "RCUR"
    LSQU = "LSQU"
    RSQU = "RSQU"
    SEMICOLON = "SEMICOLON"
    COMMA = "COMMA"
    DOT = "DOT"
    EOF = "EOF"

KEYWORDS: dict[str, TokenType] = {
    "class": TokenType.CLASS,
    "public": TokenType.PUBLIC,
    "static": TokenType.STATIC,
    "void": TokenType.VOID,
    "int": TokenType.INT,
    "float": TokenType.FLOAT,
    "boolean": TokenType.BOOLEAN_TYPE,
    "char": TokenType.CHAR,
    "String": TokenType.STRING_TYPE,
    "if": TokenType.IF,
    "else": TokenType.ELSE,
    "while": TokenType.WHILE,
    "for": TokenType.FOR,
    "return": TokenType.RETURN,
    "main": TokenType.MAIN,
    "true": TokenType.BOOLEAN,
    "false": TokenType.BOOLEAN,
}

MATH_OPERATORS: frozenset[str] = frozenset({"+", "-", "*", "/", "%"})
LOGICAL_OPERATORS: frozenset[str] = frozenset({"==", "!=", "<", ">", "<=", ">=", "&&", "||", "!"})
TWO_CHAR_OPERATORS: tuple[str, ...] = ("==", "!=", "<=", ">=", "&&", "||")
ASSIGN_OPERATOR: str = "="

DELIMITERS: dict[str, TokenType] = {
    "(": TokenType.LPAR,
    ")": TokenType.RPAR,
    "{": TokenType.LCUR,
    "}": TokenType.RCUR,
    "[": TokenType.LSQU,
    "]": TokenType.RSQU,
    ";": TokenType.SEMICOLON,
    ",": TokenType.COMMA,
    ".": TokenType.DOT,
}

@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str
    line: int
    column: int

    def format(self) -> str:
        return f"Lexeme: {self.lexeme}, Token: {self.type.value}"

    def describe(self) -> str:
        if self.type is TokenType.EOF:
            return "end of input"
        return f"'{self.lexeme}'"