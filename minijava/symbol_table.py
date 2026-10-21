from __future__ import annotations;
from dataclasses import dataclass, field;

@dataclass
class IdentifierEntry:
    """Representation of single uniqie identifier (ID) in the mini java source. """
    """
    Fields:
        index: 1-based sequential index assigned on first appearance.
        name: The exact string identifier name (case-sensitive).
        first_line: 1-based line number of first occurrence.
        first_column: 1-based column number of first occurrence.
        occurrences: List of (line, column) tuples of all occurrences.
    """

    index: int
    name: str
    first_line: int
    first_column: int
    occurrences: list[tuple[int, int]] = field(default_factory=list);


class IdentifierTable:
    """Maintains the table of unique Identifiers in order of their appearances. """
    def __init__(self) -> None:
        self._entries: dict[str, IdentifierEntry] = {}
        self._order: list[IdentifierEntry] = [];

    def add_occurrence(self, name: str, line: int, column: int) -> IdentifierEntry:
        """Records as occurrence of an Identifier (ID). """
        """If it is the first time the Identifier is seen, it creates a new entry with 
        index = len(order) + 1. If already seen before, appendes its coordinate :D
        """

        if name not in self._entries:
            entry = IdentifierEntry(
                index=len(self._order) + 1,
                name=name,
                first_line=line,
                first_column=column,
                occurrences=[(line, column)],
            )
            self._entries[name] = entry
            self._order.append(entry)
            return entry;

        entry = self._entries[name]
        entry.occurrences.append((line, column))
        return entry;

    def lookup(self, name: str) -> IdentifierEntry | None:
        """Returns the entry for an ID, or None if not found. """
        return self._entries.get(name);

    def entries(self) -> list[IdentifierEntry]:
        """Returns all entries in chronological appearence order. """
        return list(self._order);

    def __len__(self) -> int:
        """Returns total number of unique ID's. """
        return len(self._order);

    def __contains__(self, name: object) -> bool:
        """Enables the (name in table) membership checks. """
        return name in self._entries;



def format_identifier_table(table: IdentifierTable) -> str :
    """Formats the table into standard report output. 
    Example output line:
    Index: 1, Name: Student, First seen: Line 1, Columns 7, occurrences: 1
    """
    if len(table) == 0:
        return "(empty)";

    lines = []

    for entry in table.entries():
        lines.append(
            f"Index: {entry.index}, Name: {entry.name}, "
            f"First seen: line {entry.first_line}, column {entry.first_column}, "
            f"Occurrences: {len(entry.occurrences)}"
        )
    return "\n".join(lines);