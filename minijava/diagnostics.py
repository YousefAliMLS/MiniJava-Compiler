from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum

class Phase(Enum):
    LEXICAL = "lexical"
    SYNTAX = "syntax"
    SEMANTIC = "semantic"

class ErrorCode(Enum):
    LEX_INVALID_CHARACTER = "LEX_INVALID_CHARACTER"
    LEX_INVALID_IDENTIFIER = "LEX_INVALID_IDENTIFIER"
    LEX_UNCLOSED_STRING = "LEX_UNCLOSED_STRING"
    LEX_UNCLOSED_COMMENT = "LEX_UNCLOSED_COMMENT"

MESSAGE_TEMPLATES: dict[ErrorCode, str] = {
    ErrorCode.LEX_INVALID_CHARACTER: "invalid character '{lexeme}' at line {line}, column {column}.",
    ErrorCode.LEX_INVALID_IDENTIFIER: "invalid identifier '{lexeme}' at line {line}, column {column}.",
    ErrorCode.LEX_UNCLOSED_STRING: "unclosed string literal starting at line {line}, column {column}.",
    ErrorCode.LEX_UNCLOSED_COMMENT: "unclosed comment starting at line {line}, column {column}.",
}

REQUIRED_ARGS: dict[ErrorCode, tuple[str, ...]] = {
    ErrorCode.LEX_INVALID_CHARACTER: ("lexeme",),
    ErrorCode.LEX_INVALID_IDENTIFIER: ("lexeme",),
    ErrorCode.LEX_UNCLOSED_STRING: (),
    ErrorCode.LEX_UNCLOSED_COMMENT: (),
}

@dataclass
class Diagnostic:
    code: ErrorCode
    line: int
    column: int
    args: dict[str, str] = field(default_factory=dict)

    @property
    def phase(self) -> Phase:
        return Phase.LEXICAL

    def message(self) -> str:
        return MESSAGE_TEMPLATES[self.code].format(line=self.line, column=self.column, **self.args)

    def format(self) -> str:
        return "Error: " + self.message()

def make_diagnostic(code: ErrorCode, line: int, column: int, **args: str) -> Diagnostic:
    required = REQUIRED_ARGS[code]
    if set(args) != set(required):
        raise ValueError(f"{code.name} requires args {required}, got {tuple(sorted(args))}")
    return Diagnostic(code=code, line=line, column=column, args=dict(args))