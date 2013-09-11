# -*- coding: utf-8; -*-

import datetime
import urlparse
import urllib
import time
import socket

from base64 import b64encode
from httplib import HTTPConnection


class ApiError(Exception):
    def __init__(self, msg, code=None):
        super(ApiError, self).__init__(msg)
        self.code = code


class Connection(object):
    def __init__(self, account, api_key, password,
                 retry_on_503=False, retry_on_socket_error=False, retry_timeout=1):
        self.account = account
        self.api_key = api_key
        self.password = password
        self.retry_on_503 = retry_on_503
        self.retry_on_socket_error = retry_on_socket_error
        self.retry_timeout = retry_timeout

    def request(self, method, endpoint, qargs={}, data=None):
        path = self.format_path(endpoint, qargs)
        conn = HTTPConnection('%s.myinsales.ru:80' % self.account)
        auth = b64encode("%s:%s" % (self.api_key, self.password))
        headers = {
            'Authorization': 'Basic %s' % auth,
            'Content-Type': 'application/xml'
        }

        done = False
        while not done:
            try:
                conn.request(method, path, headers=headers, body=data)
            except socket.gaierror:
                if self.retry_on_socket_error:
                    time.sleep(self.retry_timeout)
                    continue
                else:
                    raise

            resp = conn.getresponse()
            body = resp.read()

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
                qargs[key] = val.strftime('%Y-%m-%d+%H:%M:%S')

        url_parts = list(urlparse.urlparse(endpoint))
        query = dict(urlparse.parse_qsl(url_parts[4]))
        query.update(qargs)
        url_parts[4] = urllib.urlencode(query)

        return urlparse.urlunparse(url_parts)

    def get(self, path, qargs):
        return self.request('GET', path, qargs=qargs)

    def put(self, path, data):
        return self.request('PUT', path, data=data)

    def post(self, path, data):
        return self.request('POST', path, data=data)

    def delete(self, path):
        return self.request('DELETE', path)
