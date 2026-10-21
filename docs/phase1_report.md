# Mini Java Compiler - Phase 1 Technical Report: Lexical Analyzer

**Course:** CSCI415 - Compiler Design (Fall 2026)  
**Deliverable:** Phase 1 Submission Report  
**Target Language:** Mini Java  
**Implementation:** Python (Standard Library Only)  

---

## 1. Tokens Implemented

Our lexical analyzer scans the Mini Java source character-by-character without relying on external or regular expression libraries. The token system supports the following categories:

### 1.1 Keywords (15 Total)
The scanner recognizes all 15 required keywords and maps them to their respective token types:
- Control Flow: `if` (`IF`), `else` (`ELSE`), `while` (`WHILE`), `return` (`RETURN`)
- Type Declarations: `boolean` (`BOOLEAN_TYPE`), `int` (`INT_TYPE`), `float` (`FLOAT_TYPE`), `String` (`STRING_TYPE`), `void` (`VOID`)
- Object-Oriented: `class` (`CLASS`), `public` (`PUBLIC`), `static` (`STATIC`), `extends` (`EXTENDS`), `this` (`THIS`), `new` (`NEW`)
- Entry Point: `main` (`MAIN`)

### 1.2 Literals
- **Numeric Literals (`NUMBER`):** Integer sequences (`42`, `0`) and floating-point literals with mandatory digits on both sides of the decimal (`3.14`, `0.5`).
- **Boolean Literals (`BOOLEAN`):** `true` and `false`.
- **String Literals (`STRING`):** Enclosed in double or single quotes with quotes preserved (`"hello"`).

### 1.3 Identifiers (`IDENTIFIER`)
Identifer names start with an ASCII letter or underscore (`[a-zA-Z_]`) followed by letters, digits, or underscores (`[a-zA-Z0-9_]*`). Every encountered identifier is registered into an `IdentifierTable` tracking 1-based first appearance coordinates and all occurrences.

### 1.4 Operators and Delimiters
- **Mathematical Operators (`MATHOP`):** `+`, `-`, `*`, `/`, `%`
- **Logical and Relational Operators (`LOGOP`):** `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `||`, `!`
- **Assignment Operator (`ASSIGN`):** `=`
- **Delimiters:** `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `.`
- **End of File:** An explicit `EOF` token emitted at the end of every stream for Phase 2 parser compatibility.

---

## 2. How Errors Were Handled

The lexical analyzer follows a non-halting error recovery strategy: when a lexical defect is detected, a descriptive diagnostic is recorded with exact 1-based coordinates (`line`, `column`), and the scanner advances to process subsequent characters. This ensures all errors in a file are captured in a single run.

Four distinct lexical errors are detected:
1. **Invalid Characters (`LEX_INVALID_CHARACTER`):** Characters not belonging to the Mini Java alphabet (such as `@`, `#`, `$`) are reported with their line and column. The scanner skips the invalid character and continues.
2. **Invalid Identifiers (`LEX_INVALID_IDENTIFIER`):** Identifiers incorrectly prefixed by digits (e.g., `1variable`, `99count`). The scanner consumes the entire malformed lexeme to prevent cascaded errors and reports the defect without emitting an identifier token.
3. **Unclosed String Literals (`LEX_UNCLOSED_STRING`):** Strings reaching a newline or EOF before the matching closing quote are flagged with the starting coordinate of the opening quote.
4. **Unclosed Multi-line Comments (`LEX_UNCLOSED_COMMENT`):** Block comments (`/* ... */`) that reach EOF without a closing `*/` report an error at the exact line and column where the comment began.

---

## 3. Challenges Faced and Solutions

### 3.1 Maximal Munch for Multi-Character Operators
- **Challenge:** Differentiating between `=` and `==`, `&` and `&&`, `|` and `||`, `<` and `<=`, `>` and `>=`.
- **Solution:** Implemented maximal munch: the scanner peeks at the subsequent character to check if a valid two-character operator exists. If so, both characters are consumed; otherwise, only the single-character operator is emitted. Lone `&` and `|` are reported as invalid characters since Mini Java does not support bitwise operators.

### 3.2 Distinguishing Floating-Point Dots from Delimiter Dots
- **Challenge:** The `.` character serves as both a method invocation delimiter (`System.out.println`) and a decimal point in float literals (`3.14`).
- **Solution:** A dot is treated as part of a numeric literal only when immediately preceded by digits and immediately followed by at least one digit (`c in "0123456789"`). In all other contexts, it is emitted as a `DOT` delimiter.

### 3.3 Digit-Prefixed Invalid Identifiers
- **Challenge:** When encountering `1name`, scanning `1` as a number and `name` as an identifier produces incorrect syntax tokens.
- **Solution:** The scanner looks ahead after consuming digits. If the character immediately following the number is an ASCII letter or underscore, the scanner consumes the entire token as a unit and emits a single `LEX_INVALID_IDENTIFIER` error.

### 3.4 Unclosed Comment Coordinate Tracking
- **Challenge:** When a multi-line comment spans dozens of lines and fails to terminate, reporting the error at EOF is unhelpful.
- **Solution:** The scanner stores the exact starting `line` and `column` when encountering `/*`. If EOF is reached before closing, the error points directly back to the opening `/*`.
