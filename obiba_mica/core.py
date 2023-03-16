"""
Based on PyCurl http://pycurl.sourceforge.net/
See also http://www.angryobjects.com/2011/10/15/http-with-python-pycurl-by-example/
Curl options http://curl.haxx.se/libcurl/c/curl_easy_setopt.html
"""

import pycurl
import base64
import json
import os.path
import getpass
import urllib.request, urllib.parse, urllib.error
from functools import reduce


class MicaClient:
    """
    MicaClient holds the configuration for connecting to Mica.
    """

    def __init__(self, server=None):
        self.curl_options = {}
        self.headers = {}
        self.base_url = self.__ensure_entry('Mica address', server)

    @classmethod
    def build(cls, loginInfo):
        return MicaClient.buildWithAuthentication(loginInfo.data['server'], loginInfo.data['user'],
                                                  loginInfo.data['password'], loginInfo.data['otp'])

    @classmethod
    def buildWithAuthentication(cls, server, user, password, otp):
        client = cls(server)
        if client.base_url.startswith('https:'):
            client.verify_peer(0)
            client.verify_host(0)
        client.credentials(user, password, otp)
        return client

    def __ensure_entry(self, text, entry, pwd=False):
        e = entry
        if not entry:
            if pwd:
                e = getpass.getpass(prompt=text + ': ')
            else:
                e = input(text + ': ')
        return e

    def credentials(self, user, password, otp):
        u = self.__ensure_entry('User name', user)
        p = self.__ensure_entry('Password', password, True)
        if otp:
            val = input("Enter 6-digits code: ")
            self.header('X-Obiba-TOTP', val)
        return self.header('Authorization', 'Basic ' + base64.b64encode((u + ':' + p).encode("utf-8")).decode("utf-8"))

    def verify_peer(self, verify):
        return self.curl_option(pycurl.SSL_VERIFYPEER, verify)

    def verify_host(self, verify):
        return self.curl_option(pycurl.SSL_VERIFYHOST, verify)

    def ssl_version(self, version):
        return self.curl_option(pycurl.SSLVERSION, version)

    def curl_option(self, opt, value):
        self.curl_options[opt] = value
        return self

    def header(self, key, value):
        self.headers[key] = value
        return self

    def new_request(self):
        return MicaRequest(self)

    def close(self):
        # request to close session
        try:
            self.new_request().resource('/auth/session/_current').delete().send()
        except Exception as e:
            pass

    class LoginInfo:
        data = None

        @classmethod
        def parse(cls, args):
            data = {}
            argv = vars(args)

            if argv.get('mica'):
                data['server'] = argv['mica']
            else:
                raise ValueError('Mica server information is missing.')

            if argv.get('user') and argv.get('password'):
                data['user'] = argv['user']
                data['password'] = argv['password']
                data['otp'] = argv['otp']
            else:
                raise ValueError('Invalid login information. Requires user and password.')

            setattr(cls, 'data', data)
            return cls()

class MicaRequest:
    """
    Mica request.
    """

    def __init__(self, mica_client):
        self.client = mica_client
        self.curl_options = {}
        self.headers = {'Accept': 'application/json'}
        self._verbose = False
        self.params = None

    def curl_option(self, opt, value):
        self.curl_options[opt] = value
        return self

    def timeout(self, value):
        return self.curl_option(pycurl.TIMEOUT, value)

    def connection_timeout(self, value):
        return self.curl_option(pycurl.CONNECTTIMEOUT, value)

    def verbose(self):
        self._verbose = True
        return self.curl_option(pycurl.VERBOSE, True)

    def fail_on_error(self):
        return self.curl_option(pycurl.FAILONERROR, True)

    def header(self, key, value):
        if value:
            self.headers[key] = value
        return self

    def accept(self, value):
        return self.header('Accept', value)

    def content_type(self, value):
        return self.header('Content-Type', value)

    def accept_json(self):
        return self.accept('application/json')

    def content_type_json(self):
        return self.content_type('application/json')

    def content_type_text_plain(self):
        return self.content_type('text/plain')

    def content_type_form(self):
        return self.content_type('application/x-www-form-urlencoded')

    def method(self, method):
        if not method:
            self.method = 'GET'
        elif method in ['GET', 'DELETE', 'PUT', 'POST', 'OPTIONS']:
            self.method = method
        else:
            raise ValueError('Not a valid method: ' + method)
        return self

    def get(self):
        return self.method('GET')

    def put(self):
        return self.method('PUT')

    def post(self):
        return self.method('POST')

    def delete(self):
        return self.method('DELETE')

    def options(self):
        return self.method('OPTIONS')

    def __build_request(self):
        curl = pycurl.Curl()
        # curl options
        for o in self.client.curl_options:
            curl.setopt(o, self.client.curl_options[o])
        for o in self.curl_options:
            curl.setopt(o, self.curl_options[o])
            # headers
        hlist = []
        for h in self.client.headers:
            hlist.append(h + ": " + self.client.headers[h])
        for h in self.headers:
            hlist.append(h + ": " + self.headers[h])
        curl.setopt(pycurl.HTTPHEADER, hlist)
        if self.method:
            curl.setopt(pycurl.CUSTOMREQUEST, self.method)
        if self.resource:
            path = self.resource
            if self.params:
                path = path + '?' + urllib.parse.urlencode(self.params)
            curl.setopt(pycurl.URL, self.client.base_url + '/ws' + path)
        else:
            raise ValueError('Resource is missing')
        return curl

    def resource(self, ws):
        self.resource = ws
        return self

    def query(self, parameters):
        self.params = parameters
        return self

    def content(self, content):
        if self._verbose:
            print('* Content:')
            print(content)
        encodedContent = content.encode('utf-8')
        self.curl_option(pycurl.POST, 1)
        self.curl_option(pycurl.POSTFIELDSIZE, len(encodedContent))
        self.curl_option(pycurl.POSTFIELDS, encodedContent)
        return self

    def form(self, parameters):
        content = urllib.parse.urlencode(parameters)
        return self.content(content)

    def content_file(self, filename):
        if self._verbose:
            print('* File Content:')
            print('[file=' + filename + ', size=' + str(os.path.getsize(filename)) + ']')
        self.curl_option(pycurl.POST, 1)
        self.curl_option(pycurl.POSTFIELDSIZE, os.path.getsize(filename))
        reader = open(filename, 'rb')
        self.curl_option(pycurl.READFUNCTION, reader.read)
        return self

    def content_upload(self, filename):
        if self._verbose:
            print('* File Content:')
            print('[file=' + filename + ', size=' + str(os.path.getsize(filename)) + ']')
            # self.curl_option(pycurl.POST,1)
        self.curl_option(pycurl.HTTPPOST, [("file1", (pycurl.FORM_FILE, filename))])
        return self

    def send(self):
        curl = self.__build_request()
        hbuf = HeaderStorage()
        cbuf = Storage()
        curl.setopt(curl.WRITEFUNCTION, cbuf.store)
        curl.setopt(curl.HEADERFUNCTION, hbuf.store)
        curl.perform()
        response = MicaResponse(curl.getinfo(pycurl.HTTP_CODE), hbuf.headers, cbuf.content)
        curl.close()

        return response


class Storage:
    """
    Content storage.
    """

    def __init__(self):
        self.content = ''
        self.line = 0

    def store(self, buf):
        self.line = self.line + 1
        self.content = self.content + buf.decode("utf-8")

    def __str__(self):
        return self.contents


class HeaderStorage(Storage):
    """
    Store response headers in a dictionary: key is the header name,
    value is header value or the list of header values.
    """

    def __init__(self):
        Storage.__init__(self)
        self.headers = {}

    def store(self, buf):
        Storage.store(self, buf)
        header = buf.decode("utf-8").partition(':')
        if header[1]:
            value = header[2].rstrip().strip()
            if header[0] in self.headers:
                current_value = self.headers[header[0]]
                if isinstance(current_value, str):
                    self.headers[header[0]] = [current_value]
                self.headers[header[0]].append(value)
            else:
                self.headers[header[0]] = value


class MicaResponse:
    """
    Response from Mica: code, headers and content
    """

    def __init__(self, code, headers, content):
        self.code = code
        self.headers = headers
        self.content = content

    def as_json(self):
        if self.content is None:
            return None
        else:
            try:
                return json.loads(self.content)
            except Exception as e:
                if type(self.content) == str:
                    return self.content
                else:
                    # FIXME silently fail
                    return None

    def pretty_json(self):
        return json.dumps(self.as_json(), sort_keys=True, indent=2)

    def __str__(self):
        return self.content


class UriBuilder:
    """
    Build a valid Uri.
    """

    def __init__(self, path=[], params={}):
        self.path = path
        self.params = params

    def path(self, path):
        self.path = path
        return self

    def segment(self, seg):
        self.path.append(seg)
        return self

    def params(self, params):
        self.params = params
        return self

    def query(self, key, value):
        self.params.update([(key, value),])
        return self

    def __str__(self):
        def concat_segment(p, s):
            return p + '/' + s

        def concat_params(k):
            return urllib.parse.quote(k) + '=' + urllib.parse.quote(str(self.params[k]))

        def concat_query(q, p):
            return q + '&' + p

        p = urllib.parse.quote('/' + reduce(concat_segment, self.path))
        if len(self.params):
            q = reduce(concat_query, list(map(concat_params, list(self.params.keys()))))
            return p + '?' + q
        else:
            return p

    def build(self):
        return self.__str__()

class HTTPError(Exception):
    def __init__(self, response: MicaResponse, message: str = None):            
        # Call the base class constructor with the parameters it needs
        super().__init__(message if message else 'HTTP Error: %s' % response.code)
        self.code = response.code
        http_status = [x for x in list(HTTPStatus) if x.value == response.code][0]
        self.message = message if message else '%s: %s' % (http_status.phrase, http_status.description)
        self.error = response.as_json() if response.content else { 'code': response.code, 'status': self.message }
        # case the reported error is not a dict
        if type(self.error) != dict:
            self.error = { 'code': response.code, 'status': self.error }

    def is_client_error(self) -> bool:
        return self.code >= 400 and self.code < 500
    
    def is_server_error(self) -> bool:
        return self.code >= 500