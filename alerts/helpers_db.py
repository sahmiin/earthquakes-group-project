from __future__ import annotations
from dataclasses import dataclass


@dataclass
class FakeCursor:
    description: list = None
    executed: list = None
    _fetchall: list = None
    _fetchone: any = None

    def __post_init__(self):
        self.executed = [] if self.executed is None else self.executed
        self._fetchall = [] if self._fetchall is None else self._fetchall

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchall(self):
        return self._fetchall

    def fetchone(self):
        return self._fetchone

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


@dataclass
class FakeConn:
    cursor_obj: FakeCursor

    def cursor(self):
        return self.cursor_obj

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False
