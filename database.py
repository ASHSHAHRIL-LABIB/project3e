import sqlite3


class SQLiteConnectionAdapter:
    def __init__(self, connection):
        self._connection = connection

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self._connection.__exit__(exc_type, exc_value, traceback)

    def execute(self, *args, **kwargs):
        return self._connection.execute(*args, **kwargs)

    def executescript(self, *args, **kwargs):
        return self._connection.executescript(*args, **kwargs)


class DatabaseFactory:
    def __init__(self, path):
        self.path = path

    def connect(self):
        return SQLiteConnectionAdapter(sqlite3.connect(self.path))
