
import json

from . import error
from . import strings as ustr


try:
    from http import client as http
    from urllib.parse import urlparse
except ImportError: # python 2.x compat
    import httplib as http
    from urlparse import urlparse

TX_ENDPOINT = "/db/data/transaction"
TX_COMMIT_ENDPOINT = "/db/data/transaction/commit"


def neo_code_to_error_class(code):
    if code.startswith('Neo.ClientError.Schema'):
        return error.IntegrityError
    elif code.startswith('Neo.ClientError'):
        return error.ProgrammingError
    else:
        return error.InternalError


def default_error_handler(connection, cursor, errorclass, errorvalue):
    if errorclass != Connection.Warning:
        raise errorclass(errorvalue)


class Connection(object):

    _COMMON_HEADERS = {"Content-Type": "application/json", "Accept": "application/json", "Connection": "keep-alive"}

    def __init__(self, db_url):
        self._host = urlparse(db_url).netloc
        self._http = http.HTTPConnection(self._host)


    # afaict we don't use this
    def close(self):
        if self._http is not None:
            self._http.close()
            self._http = None


    def __del__(self):
        self.close()


    def _commit_request(self, statement, **kwargs):

        payload = [ {'statement': statement, 'parameters': kwargs} ]

        http_response = self._request("POST", TX_COMMIT_ENDPOINT, {'statements': payload})

        # copied from below
        response = self._deserialize(http_response)
        self._handle_errors(response)
        return self._extract_rows(response)


    def _tx_request(self, tx, statement, **kwargs):
        """"
        Executes a list of statements, returning an iterator of results sets. Each 
        statement should be a tuple of (statement, params).
        """
        payload = [ {'statement': statement, 'parameters':  kwargs} ]
        http_response = self._request('POST', tx, {'statements': payload})

        tx_url = http_response.getheader('Location')

        response = self._deserialize(http_response)
        self._handle_errors(response)
        return self._extract_rows(response), tx_url


    def _request(self, method, path, payload=None):
        serialized_payload = json.dumps(payload) if payload is not None else None

        try:
            self._http.request(method, path, serialized_payload, self._COMMON_HEADERS)
            http_response = self._http.getresponse()
        except (http.BadStatusLine, http.CannotSendRequest) as e:
            raise Connection.OperationalError('Connection error: ' + str(e))

        if not http_response.status in [200, 201]:
            raise error.OperationalError('Server returned unexpected response: ' + ustr(http_response.status) + ' ' + ustr(http_response.read()))

        return http_response


    def _handle_errors(self, response):
        # do we ever got more than one here? - I hope not
        for err in response['errors']:
            error_class = neo_code_to_error_class(err['code'])
            error_value = ustr(error['code']) + ": " + ustr(err['message'])
            raise error_class(error_value)


    def _extract_rows(self, response):
        results = response['results']
        if not results:
            return []
        else:
            return [ d['row'] for d in results[0]['data'] ]


    def _deserialize(self, response):
        # TODO: This is exceptionally annoying, python 3 has improved byte array handling, but that means the JSON
        # parser no longer supports deserializing these things in a streaming manner, so we have to decode the whole
        # thing first.
        return json.loads(response.read().decode('utf-8'))
