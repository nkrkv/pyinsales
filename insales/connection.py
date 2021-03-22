# -*- coding: utf-8; -*-

import datetime
import time
import threading
import socket

from base64 import b64encode

try:
    # Python 3
    from urllib import parse as urlparse
    from urllib.parse import urlencode
    from http.client import HTTPConnection, HTTPSConnection, HTTPException
except ImportError:
    # Python 2
    import urlparse
    from httplib import HTTPConnection, HTTPSConnection, HTTPException
    from urllib import urlencode


insales_lock = threading.Lock()


def throttle_fn(curr: int, limit: int):
    return 0.1 + (1.0 - (limit - curr)/limit)**16 * 8.5


class ApiError(Exception):
    def __init__(self, msg, code=None):
        super(ApiError, self).__init__(msg)
        self.code = code


class Connection(object):
    def __init__(self, account, api_key, password,
                 secure=False,
                 retry_on_503=False, retry_on_socket_error=False,
                 retry_timeout=1, response_timeout=10,
                 throttle=False):
        self.account = account
        self.api_key = api_key
        self.password = password
        self.secure = secure
        self.retry_on_503 = retry_on_503
        self.retry_on_socket_error = retry_on_socket_error
        self.retry_timeout = datetime.timedelta(seconds=retry_timeout)
        self.response_timeout = response_timeout
        self.last_req_time = datetime.datetime.now()
        self.retry_after = datetime.datetime.now()
        self.max_wait_time = datetime.timedelta(seconds=60)
        self.throttle = throttle != False
        self.throttle_fn = throttle if callable(throttle) else throttle_fn

    def get_retry_after(self):
        return self.retry_after

    def _set_retry_after(self, delta):
        with insales_lock:
            self.retry_after = self.last_req_time + min(
                delta, self.max_wait_time
            )

    def _increase_retry_after(self, delta):
        with insales_lock:
            self.retry_after = max(self.last_req_time, self.retry_after) + min(
                delta, self.max_wait_time
            )

    def _apply_retry_timeout(self):
        self._set_retry_after(self.retry_timeout)

    def _handle_retry_after_header(self, header):
        try:
            self._set_retry_after(datetime.timedelta(seconds=int(header)))
        except ValueError:
            self._apply_retry_timeout()

    def _apply_usage_limit(self, header):
        if header is None:
            return

        try:
            curr_str, limit_str = header.split("/")
            delta = datetime.timedelta(seconds=self.throttle_fn(
                int(curr_str),
                int(limit_str),
            ))
            self._increase_retry_after(delta)
        except ValueError:
            pass

    def _wait_until_retry_after(self):
        delta = self.retry_after - datetime.datetime.now()
        if delta.total_seconds() > 0:
            time.sleep(delta.total_seconds())


    def request(self, method, endpoint, qargs={}, data=None):
        path = self.format_path(endpoint, qargs)
        auth = b64encode(u"{0}:{1}".format(self.api_key, self.password).encode('utf-8')).decode('utf-8')
        headers = {
            'Authorization': 'Basic {0}'.format(auth),
            'Content-Type': 'application/xml'
        }

        done = False
        while not done:
            self._wait_until_retry_after()
            try:
                host = '%s.myinsales.ru' % self.account
                if self.secure:
                    conn = HTTPSConnection(host, timeout=self.response_timeout)
                else:
                    conn = HTTPConnection(host, timeout=self.response_timeout)
                with insales_lock:
                    self.last_req_time = datetime.datetime.now()
                conn.request(method, path, headers=headers, body=data)
                resp = conn.getresponse()
                body = resp.read()
            except (socket.gaierror, socket.timeout, HTTPException):
                if self.retry_on_socket_error:
                    self._apply_retry_timeout()
                    continue
                else:
                    raise

            if self.throttle:
                self._apply_usage_limit(resp.getheader('API-Usage-Limit'))

            if resp.status == 503 and self.retry_on_503:
                retry_after_header = resp.getheader('Retry-After')
                if retry_after_header:
                    self._handle_retry_after_header(retry_after_header)
                else:
                    self._apply_retry_timeout()
            else:
                done = True

        if 200 <= resp.status < 300:
            return body
        else:
            raise ApiError(
                "{} request to {} returned: {}\n{}".format(
                    method,
                    path,
                    resp.status,
                    body.decode('utf-8') if type(body) == bytes else body
                ),
                resp.status
            )

    def format_path(self, endpoint, qargs):
        for key, val in qargs.items():
            if isinstance(val, datetime.datetime):
                qargs[key] = val.replace(microsecond=0).isoformat()

        url_parts = list(urlparse.urlparse(endpoint))
        query = urlparse.parse_qsl(url_parts[4])
        for key, value in qargs.items():
            if isinstance(value, list):
                for sub_val in value:
                    query.append((f"{key}[]", sub_val))
            else:
                query.append((key, value))
        url_parts[4] = urlparse.urlencode(query)

        return urlparse.urlunparse(url_parts)

    def get(self, path, qargs):
        return self.request('GET', path, qargs=qargs)

    def put(self, path, data):
        return self.request('PUT', path, data=data)

    def post(self, path, data):
        return self.request('POST', path, data=data)

    def delete(self, path):
        return self.request('DELETE', path)
