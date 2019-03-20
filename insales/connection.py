# -*- coding: utf-8; -*-

import datetime
import time
import socket

from base64 import b64encode

try:
    # Python 3
    from urllib import parse as urlparse
    from urllib.parse import urlencode
    from http.client import HTTPConnection, HTTPException
except ImportError:
    # Python 2
    import urlparse
    from httplib import HTTPConnection, HTTPException
    from urllib import urlencode


class ApiError(Exception):
    def __init__(self, msg, code=None):
        super(ApiError, self).__init__(msg)
        self.code = code


class Connection(object):
    def __init__(self, account, api_key, password,
                 retry_on_503=False, retry_on_socket_error=False,
                 retry_timeout=1, response_timeout=10):
        self.account = account
        self.api_key = api_key
        self.password = password
        self.retry_on_503 = retry_on_503
        self.retry_on_socket_error = retry_on_socket_error
        self.retry_timeout = retry_timeout
        self.response_timeout = response_timeout

    def request(self, method, endpoint, qargs={}, data=None):
        path = self.format_path(endpoint, qargs)
        auth = b64encode(u"{0}:{1}".format(self.api_key, self.password).encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': 'Basic {0}'.format(auth),
            'Content-Type': 'application/xml'
        }

        done = False
        while not done:
            try:
                conn = HTTPConnection('%s.myinsales.ru:80' % self.account,
                                      timeout=self.response_timeout)
                conn.request(method, path, headers=headers, body=data)
                resp = conn.getresponse()
                body = resp.read()
            except (socket.gaierror, socket.timeout, HTTPException):
                if self.retry_on_socket_error:
                    time.sleep(self.retry_timeout)
                    continue
                else:
                    raise

            if resp.status == 503 and self.retry_on_503:
                time.sleep(self.retry_timeout)
            else:
                done = True

        if 200 <= resp.status < 300:
            return body
        else:
            raise ApiError("%s request to %s returned: %s\n%s" %
                           (method, path, resp.status, body), resp.status)

    def format_path(self, endpoint, qargs):
        for key, val in qargs.items():
            if isinstance(val, datetime.datetime):
                qargs[key] = val.replace(microsecond=0).isoformat()

        url_parts = list(urlparse.urlparse(endpoint))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(qargs)
        url_parts[4] = urlencode(query)

        return urlparse.urlunparse(url_parts)

    def get(self, path, qargs):
        return self.request('GET', path, qargs=qargs)

    def put(self, path, data):
        return self.request('PUT', path, data=data)

    def post(self, path, data):
        return self.request('POST', path, data=data)

    def delete(self, path):
        return self.request('DELETE', path)
