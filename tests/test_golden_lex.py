import io
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from minijava.driver import main

GOLDEN_DIR = Path(__file__).parent / "golden" / "lex"


class TestGoldenLex(unittest.TestCase):
    def test_golden_files_exist(self):
        self.assertGreaterEqual(len(list(GOLDEN_DIR.glob("*.mj"))), 15)


def _make_test(mj: Path):
    def test(self):
        out_file = mj.with_suffix(".out")
        self.assertTrue(out_file.is_file(), f"missing {out_file.name}")
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = main([str(mj)])
        self.assertEqual(buf.getvalue(), out_file.read_text(encoding="utf-8"))
        expect_ok = "completed successfully" in out_file.read_text(encoding="utf-8")
        self.assertEqual(code, 0 if expect_ok else 1)
    return test


for _mj in sorted(GOLDEN_DIR.glob("*.mj")):
    setattr(TestGoldenLex, f"test_{_mj.stem}", _make_test(_mj))

if __name__ == "__main__":
    unittest.main()
