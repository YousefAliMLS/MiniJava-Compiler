# Mini Java Compiler (CSCI415 - Fall 2026)

[![Language](https://img.shields.io/badge/Language-Python%203.10%2B-blue.svg)](https://www.python.org/)
[![Course](https://img.shields.io/badge/Course-CSCI415%20Compiler%20Design-green.svg)](Projects/ProjectGuidelinesAndDetails.pdf)
[![Phase](https://img.shields.io/badge/Phase-01%20Lexical%20Analysis%20(Active)-orange.svg)](Projects/Phase%201/)
[![License](https://img.shields.io/badge/License-Academic%20Integrity-red.svg)](Projects/ProjectGuidelinesAndDetails.pdf)
[![Standard Library](https://img.shields.io/badge/Dependencies-Standard%20Library%20Only-brightgreen.svg)](Projects/Phase%201/SHARED_PROJECT_CONTRACT.md)

A modular, hand-crafted compiler front-end for **Mini Java** (a simplified, statically-typed Java-like language), developed for **CSCI415: Compiler Design** at university.

The project is structured into three progressive phases:
- **Phase 01: Lexical Analyzer (Scanner)** - *Active* (Deadline: **October 30, 2026**)
- **Phase 02: Syntax Analyzer (Parser)** - *Starts Nov 21, 2026*
- **Phase 03: Semantic Analyzer (Type & Scope Checker)** - *Starts Nov 21, 2026*

---

## Table of Contents
- [Project Overview](#project-overview)
- [Phase 1: Lexical Analysis Scope](#phase-1-lexical-analysis-scope)
- [Team Roles and Task Allocation](#team-roles-and-task-allocation)
- [Repository Structure](#repository-structure)
- [Installation and Execution](#installation-and-execution)
- [Diagnostic and Error Handling](#diagnostic-and-error-handling)
- [Testing Strategy](#testing-strategy)
- [Academic Integrity Notice](#academic-integrity-notice)

---

## Project Overview

Mini Java is a case-sensitive, object-oriented language supporting primitive types (`int`, `float`, `boolean`, `char`, `String`), single-dimensional arrays, arithmetic and relational expressions, control flow (`if`/`else`, `while`, `for`), and class/method declarations.

### Core Architectural Principles
1. **Zero External Dependencies:** Built purely using the Python standard library (`dataclasses`, `enum`, `typing`).
2. **No Ready-Made Generators:** In strict compliance with official course guidelines (*PDF p. 1*), the scanner and parser are built completely by hand (no `re` regular expressions, `ply`, `lark`, or `antlr4`).
3. **Forward Compatibility:** The Phase 1 token definitions and symbol table are architected to feed directly into Phase 2 and Phase 3 without refactoring.

---

## Phase 1: Lexical Analysis Scope

The Phase 1 scanner converts raw source code character-by-character into a stream of tokens while tracking 1-based source coordinates (`line` and `column`):

- **Keywords (15):** `class`, `public`, `static`, `void`, `int`, `float`, `boolean`, `char`, `String`, `if`, `else`, `while`, `for`, `return`, `main`.
- **Literals:**
  - `NUMBER`: Integer and floating-point numeric literals (e.g., `10`, `85.5`).
  - `STRING`: Single and double-quoted strings (e.g., `"Ali"`, `'A'`).
  - `BOOLEAN`: Boolean literals `true` and `false`.
- **Operators:**
  - `MATHOP`: `+`, `-`, `*`, `/`, `%`
  - `LOGOP`: `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!` (Maximal Munch prioritized)
  - `ASSIGN`: `=`
- **Delimiters:** `(`, `)`, `{`, `}`, `[`, `]`, `;`, `,`, `.`
- **Comments:** Single-line `//` and multi-line `/* ... */` are stripped.
- **Identifier Table:** Maintains an index of all user-defined identifiers, their first occurrence, and subsequent coordinate occurrences.

---

## Team Roles and Task Allocation (Team 9)

Work is divided across five distinct roles to ensure balanced implementation:

| Member | Primary Responsibility | Owned Files | Deliverables |
|---|---|---|---|
| **Member 1**<br>Hamza Taher Essam<br>`231001880` | **Architect & CLI Integration Lead** | `minijava/tokens.py`<br>`minijava/diagnostics.py`<br>`minijava/driver.py`<br>`tests/helpers.py`<br>`tests/test_contract.py` | Token definitions, diagnostic factory, CLI driver, report formatter, and reflection tests. |
| **Member 2**<br>Mostafa Abd Elhamied Ismael<br>`231000842` | **Lexer Engine Core** | `minijava/lexer.py`<br>`tests/test_lexer_core.py` | Central `Lexer` loop, cursor navigation, whitespace, comments, delimiters, and EOF token. |
| **Member 3**<br>Yousef Mahmoud Ali (Lead)<br>`231001086` | **Symbol Table & Submission Lead** | `minijava/symbol_table.py`<br>`tests/test_symbol_table.py`<br>`samples/phase1_tests.txt`<br>`docs/phase1_report.md` | `IdentifierTable`, formatting, test programs deliverable, and official 1-2 page technical report. |
| **Member 4**<br>Yosef Mohamed Yacoup<br>`231000016` | **Scanner Specialist: Identifiers & Numbers** | `minijava/scanner_ident_num.py`<br>`tests/test_scanner_ident_num.py`<br>`tests/test_pdf_examples.py` | Identifiers, keywords, float/int literals, digit-prefixed invalid identifier detection (`1name`), PDF regression suite. |
| **Member 5**<br>Youssef Hassan Nasr<br>`231000751` | **Scanner Specialist: Strings & Operators** | `minijava/scanner_str_op.py`<br>`tests/test_scanner_str_op.py`<br>`tests/golden/lex/*` | String literals, escape sequences, operator maximal munch, and independent golden test cases. |

---

## Repository Structure

```
CompilerProject/
├── README.md                             # Project overview and CLI documentation
├── .gitignore                            # Python bytecode and workspace ignore rules
├── Projects/
│   ├── ProjectGuidelinesAndDetails.pdf   # Official course specification
│   └── Phase 1/                          # Phase 1 planning documents and AI prompts
│       ├── PROJECT_REQUIREMENTS_ANALYSIS.md
│       ├── PROJECT_ARCHITECTURE_AND_TEAM_PLAN.md
│       ├── SHARED_PROJECT_CONTRACT.md    # Binding technical contract (single source of truth)
│       ├── AI_PROMPT_MEMBER_1.md         # Implementation prompt for Member 1
│       ├── AI_PROMPT_MEMBER_2.md         # Implementation prompt for Member 2
│       ├── AI_PROMPT_MEMBER_3.md         # Implementation prompt for Member 3
│       ├── AI_PROMPT_MEMBER_4.md         # Implementation prompt for Member 4
│       ├── AI_PROMPT_MEMBER_5.md         # Implementation prompt for Member 5
│       ├── INTEGRATION_AND_TESTING_PLAN.md
│       └── PROJECT_RISK_AND_FINAL_AUDIT.md
├── minijava/
│   ├── __init__.py                       # Package metadata
│   ├── __main__.py                       # CLI entrypoint
│   ├── tokens.py                         # TokenType enum and Token dataclass
│   ├── diagnostics.py                    # Diagnostic engine and error codes
│   ├── driver.py                         # CLI reader, phase runner, and report formatter
│   ├── lexer.py                          # Hand-crafted scanner engine
│   ├── symbol_table.py                   # IdentifierTable and formatting
│   ├── scanner_ident_num.py              # Identifiers, keywords, numbers, invalid ids
│   └── scanner_str_op.py                 # String literals and operator maximal munch
├── tests/
│   ├── helpers.py                        # In-process test runner and fixtures
│   ├── test_contract.py                  # Reflection contract conformance suite
│   ├── test_driver.py                    # CLI and exit code tests
│   ├── test_lexer_core.py                # Core scanner unit tests
│   ├── test_symbol_table.py              # Symbol table unit tests
│   ├── test_scanner_ident_num.py         # Identifier and number tests
│   ├── test_scanner_str_op.py            # String and operator tests
│   ├── test_pdf_examples.py              # Exact PDF p. 3-5 regression suite
│   └── golden/lex/                       # Independent golden test cases (*.mj + *.out)
├── samples/
│   └── phase1_tests.txt                  # Official test input programs deliverable
└── docs/
    └── phase1_report.md                  # Official 1-2 page technical report deliverable
```

---

## Installation and Execution

### Requirements
- **Python ≥ 3.10** (standard library only)

### Byte-Compile Check
```bash
python3 -m compileall -q minijava tests
```

### Running the Lexer
```bash
# Basic Phase 1 lexical scan
python3 -m minijava samples/phase1_tests.txt --phase lex

# Display individual token stream
python3 -m minijava samples/phase1_tests.txt --phase lex --tokens

# Display symbol table
python3 -m minijava samples/phase1_tests.txt --phase lex --symbols
```

---

## Diagnostic and Error Handling

All diagnostics report 1-based coordinates with descriptive messages matching the course guidelines (*PDF p. 3-4*):

```
Error: invalid character '@' at line 1, column 12.
Error: invalid identifier '1name' at line 1, column 1.
Error: unclosed string literal starting at line 1, column 15.
Error: unclosed comment starting at line 1, column 1.
```

---

## Testing Strategy

The repository includes a comprehensive 4-layer testing suite:

```bash
# Run all tests
python3 -m unittest discover -s tests -v

# Run contract reflection verification
python3 -m unittest tests.test_contract -v

# Run official PDF p. 3-5 acceptance suite
python3 -m unittest tests.test_pdf_examples -v
```

---

## Academic Integrity Notice

This project is an original clean-room implementation created for **CSCI415 Compiler Design**. In accordance with university policy:
- No code has been copied from third-party or student repositories.
- No ready-made lexical analyzer or parser generators (Lex, Flex, ANTLR, PLY, Lark) are used.
- All team members participate in active code development and are prepared for oral examination.
