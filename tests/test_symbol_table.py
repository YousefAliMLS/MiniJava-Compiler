from __future__ import annotations;
import unittest;

from minijava.symbol_table import(
    IdentifierEntry,
    IdentifierTable,
    format_identifier_table
)

class TestIdentifierTable(unittest.TestCase):
    """"Unit tests for IdentifierTable and format Identifier table. """

    def setUp(self) ->  None:
        self.table = IdentifierTable()

    def test_empty_table(self) -> None:
        """An empty table must have length 0 and outputs as: (empty). """
        self.assertEqual(len(self.table), 0)
        self.assertEqual(self.table.entries(), [])
        self.assertIsNone(self.table.lookup("Yousef"))
        self.assertNotIn("Yousef", self.table)
        self.assertEqual(format_identifier_table(self.table), "(empty)")

    def test_add_single_occurrence(self) -> None:
        """First occurrence receives index 1 and records coordinates."""
        entry = self.table.add_occurrence("x", line=1, column=5)
        self.assertEqual(entry.index, 1)
        self.assertEqual(entry.name, "x")
        self.assertEqual(entry.first_line, 1)
        self.assertEqual(entry.first_column, 5)
        self.assertEqual(entry.occurrences, [(1, 5)])
        self.assertEqual(len(self.table), 1)
        self.assertIn("x", self.table)
    def test_add_multiple_occurrences_same_name(self) -> None:
        """Repeated identifiers reuse the existing entry and append coordinates."""
        self.table.add_occurrence("count", line=2, column=10)
        self.table.add_occurrence("count", line=5, column=12)
        self.table.add_occurrence("count", line=8, column=3)
        self.assertEqual(len(self.table), 1)
        entry = self.table.lookup("count")
        self.assertIsNotNone(entry)
        self.assertEqual(entry.index, 1)
        self.assertEqual(entry.first_line, 2)
        self.assertEqual(entry.first_column, 10)
        self.assertEqual(entry.occurrences, [(2, 10), (5, 12), (8, 3)])
    def test_multiple_distinct_identifiers_order(self) -> None:
        """Distinct identifiers get sequential 1-based indices in appearance order."""
        e1 = self.table.add_occurrence("first", line=1, column=1)
        e2 = self.table.add_occurrence("second", line=1, column=10)
        e3 = self.table.add_occurrence("third", line=2, column=5)
        self.assertEqual(e1.index, 1)
        self.assertEqual(e2.index, 2)
        self.assertEqual(e3.index, 3)
        self.assertEqual(len(self.table), 3)
        names = [e.name for e in self.table.entries()]
        self.assertEqual(names, ["first", "second", "third"])
    def test_case_sensitivity(self) -> None:
        """Identifiers with different casing must be stored as separate entries."""
        self.table.add_occurrence("Student", line=1, column=1)
        self.table.add_occurrence("student", line=2, column=1)
        self.table.add_occurrence("STUDENT", line=3, column=1)
        self.assertEqual(len(self.table), 3)
        self.assertIn("Student", self.table)
        self.assertIn("student", self.table)
        self.assertIn("STUDENT", self.table)
    def test_lookup_nonexistent(self) -> None:
        """Lookup returns None for unseen identifier."""
        self.table.add_occurrence("alpha", line=1, column=1)
        self.assertIsNone(self.table.lookup("beta"))
    def test_format_identifier_table_output(self) -> None:
        """Formatted output matches PDF specification format."""
        self.table.add_occurrence("Student", line=1, column=7)
        self.table.add_occurrence("total", line=3, column=15)
        self.table.add_occurrence("total", line=6, column=20)
        expected = (
            "Index: 1, Name: Student, First seen: line 1, column 7, Occurrences: 1\n"
            "Index: 2, Name: total, First seen: line 3, column 15, Occurrences: 2"
        )
        self.assertEqual(format_identifier_table(self.table), expected)
if __name__ == "__main__":
    unittest.main()