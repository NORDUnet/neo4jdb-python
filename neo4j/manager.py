"""
Connection manager. Use this in your client.

It does (or should) do connecting pooling.

Use .request for single requests.

Use with manager.transaction as t for transactions.

Fork of jakewins/neo4jdb-python.
"""

from contextlib import contextmanager

from neo4j.connection import Connection
from neo4j.transaction import Transaction



class ConnectionManager():

    """
    Neo4jDBConnectionManager.transaction()
    When we don't want to share a connection (transaction context) we can set up a new connection which will work
    just as the write context manager above but with it's own connection.

    >>> n4cm = Neo4jDBConnectionManager("http://localhost:7474")
    >>> n4cm.request("CREATE (TheMatrix:Movie {title:'The Matrix', tagline:'Welcome to the Real World'})")
    [ whatever ]
    >>>
    >>> for n in n4cm.request("MATCH (n:Movie) RETURN n LIMIT 1"):
    ...     print n
    "({'tagline': 'Welcome to the Real World', 'title': 'The Matrix'},)"

    Commits in batches can be achieved by:
    >>> with manager.transaction() as tr:
    ...     w.execute("CREATE (TheMatrix:Movie {title:'The Matrix Reloaded', tagline:'Free your mind.'})")
    ...     w.execute("CREATE (TheMatrix:Movie {title:'Matrix Revolutions', tagline:'Everything that has a beginning has an end.'})")
    ...     w.connection.commit()
    """

    def __init__(self, dsn):
        self.dsn = dsn
        self.free_connections = []


    def _new_connection(self):
        conn = Connection(self.dsn)
        return conn


    def _get_connection(self):
        try:
            conn = self.free_connections.pop()
        except IndexError:
            conn = self._new_connection()

        return conn


    def _release_connection(self, conn):
        self.free_connections.append(conn)


    def request(self, statement, *kwargs):
        # A single request, that runs in its own transaction
        # Can be read or write. Does not matter.
        # If you want multiple statements in a single transaction, using the with transaction as t...
        assert type(statement) in (bytes, str), 'Statement must be a string'
        conn = self._get_connection()
        result = conn._commit_request(statement)
        self._release_connection(conn)
        return result


    @contextmanager
    def _transaction(self):
        tr = Transaction(self._get_connection())
        try:
            yield tr
        finally:
            tr.done()
            self._release_connection(tr._conn)

    transaction = property(_transaction)

