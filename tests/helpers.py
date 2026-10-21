from __future__ import annotations
import sys
from io import StringIO
from minijava.driver import main
from minijava.lexer import tokenize, LexResult

def run_cli(args: list[str]) -> tuple[int, str, str]:
    """Runs minijava.driver.main() in-process, capturing stdout and stderr.
    Returns (exit_code, stdout_str, stderr_str).
    """
    old_argv = sys.argv
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    
    sys.argv = ["python3 -m minijava"] + args
    sys.stdout = StringIO()
    sys.stderr = StringIO()
    
    exit_code = 0
    try:
        exit_code = main()
    except SystemExit as e:
        exit_code = e.code if isinstance(e.code, int) else 1
    except Exception:
        exit_code = 2
    finally:
        out_str = sys.stdout.getvalue()
        err_str = sys.stderr.getvalue()
        sys.argv = old_argv
        sys.stdout = old_stdout
        sys.stderr = old_stderr
        
    return exit_code, out_str, err_str

def lex(source: str) -> LexResult:
    """Helper shortcut to tokenize source strings directly in tests."""
    return tokenize(source)