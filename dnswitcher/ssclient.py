# coding: utf8

from shadowsocks import encrypt
import urllib
import httplib
from httplib import HTTPConnection, HTTPSConnection, HTTP, HTTPS
import struct

BUF_SIZE = 1024


class SSHTTPConnection(HTTPConnection):
    def __init__(self, *args, **kwargs):
        self.ss_client = kwargs.pop('ss_client')
        HTTPConnection.__init__(self, *args, **kwargs)

    def send(self, data):
        data = self.ss_client.encrypt(data)
        HTTPConnection.send(self, data)

    def putrequest(self, method, url, skip_host=0, skip_accept_encoding=0):
        import urlparse
        parts = urlparse.urlparse(url)
        domain, port = urllib.splitport(parts.netloc)
        if not port:
            port = 80

        domain_len = len(domain)
        data = struct.pack("!BB%dsH" % domain_len, 3, domain_len, domain, port)
        self.send(data)

        HTTPConnection.putrequest(self, method, url, skip_host, skip_accept_encoding)


class SSHTTPSConnection(HTTPSConnection):
    def __init__(self, *args, **kwargs):
        self.ss_client = kwargs.pop('ss_client')
        HTTPSConnection.__init__(self, *args, **kwargs)

    def connect(self):
        HTTPConnection.connect(self)

    def send(self, data):
        data = self.ss_client.encrypt(data)
        HTTPSConnection.send(self, data)

    def putrequest(self, method, url, skip_host=0, skip_accept_encoding=0):
        import urlparse
        parts = urlparse.urlparse(url)
        domain, port = urllib.splitport(parts.netloc)
        if not port:
            port = 80

        domain_len = len(domain)
        data = struct.pack("!BB%dsH" % domain_len, 3, domain_len, domain, port)
        self.send(data)

        self.sock = self._context.wrap_socket(self.sock,
                                              server_hostname=domain)

        HTTPSConnection.putrequest(self, method, url, skip_host, skip_accept_encoding)


class SSHTTPMixin(httplib.HTTP):
    def __init__(self, ss_client):
        self._ss_client = ss_client
        self._setup(self._connection_class(ss_client.server_host,
                                           ss_client.server_port,
                                           timeout=ss_client.timeout,
                                           ss_client=ss_client))


class SSHTTP(SSHTTPMixin, HTTP):
    _connection_class = SSHTTPConnection


class SSHTTPS(SSHTTPMixin, HTTPS):
    _connection_class = SSHTTPSConnection


class SimpleSSClient(object):
    def __init__(self, server_host, server_port, password, method, timeout=10):
        self._encryptor = encrypt.Encryptor(password, method)
        self.server_host = server_host
        self.server_port = server_port
        self.timeout = timeout

    def encrypt(self, data):
        return self._encryptor.encrypt(data)

    def decrypt(self, data):
        return self._encryptor.decrypt(data)

    def get(self, url):
        schem, _ = urllib.splittype(url)
        if schem.lower() == 'https':
            # http_req = SSHTTPS(self)
            raise NotImplementedError(schem)
        else:
            http_req = SSHTTP(self)
        http_req.putrequest('GET', url)
        http_req.endheaders()

        code, _, _ = http_req.getreply()
        fd = http_req.getfile()
        if fd:
            return self.decrypt(fd.read())
        else:
            raise Exception("HTTP ERROR: %s" % code)


if __name__ == '__main__':
    def func(server_host, server_port, password, method):
        cli = SimpleSSClient(server_host, server_port, password, method)
        print cli.get('http://google.com/')

    import threading
    from functools import partial
    p_func = partial(func, server_port=22972, password='', method='rc4-md5')
    t = threading.Thread(target=p_func, args=('cn5t.hxg.cc',))
    t.start()
    t.join()

