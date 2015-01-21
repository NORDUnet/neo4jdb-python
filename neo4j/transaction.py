"""
Represents a transaction over the Neo4J transactional http interface (not really rest).
"""

try:
    from urllib.parse import urlparse
except ImportError: # python 2.x compat
    from urlparse import urlparse

from . import error, connection

# Note: Transactions are not bound to connections in neo4j, but we do it,
# as the code is simpler that way, and it is "good enough"



class Transaction:

    def __init__(self, conn):
        self._conn = conn # connection
        self._done = False
        self._tx = None # transaction (url)


    def _check_done(self):
        if self._done:
            raise error.OperationalError('Transaction is done')


    def done(self):
        self._done = True
        self._tx = None


    def execute(self, statement, **kwargs):
        self._check_done()

        if self._tx is None:
            response, tx_url = self._conn._tx_request(connection.TX_ENDPOINT, statement, **kwargs)
            self._tx = urlparse(tx_url).path
        else:
            response, _ = self._conn._tx_request(self._tx, statement, **kwargs)

        return response


    def commit(self):
        self._check_done()
        assert self._tx is not None, 'No transaction active, cannot commit'

        response = self._conn._request('POST', self._tx + "/commit")
        self.done()
        return response.read()


    def rollback(self):
        self._check_done()
        assert self._tx is not None, 'No transaction active, cannot rollack'

        response = self._conn._request('DELETE', self._tx)
        self.done()
        return response.read()

