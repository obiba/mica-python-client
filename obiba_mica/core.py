"""
Based on Python Request library https://docs.python-requests.org/en/latest/index.html
"""

import base64
import json
import os.path
import getpass
from http import HTTPStatus
import urllib.request, urllib.parse, urllib.error
from functools import reduce
from requests import Session, Request, Response
import logging

class MicaClient:
    """
    Mica Client
    """

    def __init__(self, server=None):
        self.session = Session()
        self.base_url = self.__ensure_entry('Mica address', server)

    def __del__(self):
        self.close()

    @classmethod
    def build(cls, loginInfo):
        return MicaClient.buildWithAuthentication(loginInfo.data['server'], loginInfo.data['user'],
                                                  loginInfo.data['password'], loginInfo.data['otp'])

    @classmethod
    def buildWithAuthentication(cls, server, user, password, otp):
        client = cls(server)
        if client.base_url.startswith('https:'):
            client.session.verify = False

        client.credentials(user, password, otp)
        return client

    def credentials(self, user, password, otp):
        u = self.__ensure_entry('User name', user)
        p = self.__ensure_entry('Password', password, True)
        if otp:
            val = input("Enter 6-digits code: ")
            self.session.headers.update({'X-Obiba-TOTP': val})

        self.session.headers.update({'Authorization': 'Basic %s' % base64.b64encode(('%s:%s' % (u, p)).encode("utf-8")).decode("utf-8")})

    def __ensure_entry(self, text, entry, pwd=False):
        e = entry
        if not entry:
            if pwd:
                e = getpass.getpass(prompt=text + ': ')
            else:
                e = input(text + ': ')
        return e

    def verify(self, value):
        """
        Ignore or validate certificate

        :param value = True/False to validation or not. Value can also be a CA_BUNDLE file or directory (e.g. 'verify=/etc/ssl/certs/ca-certificates.crt')
        """
        self.session.verify = value
        return self

    def header(self, key, value):
        header = {}
        header[key] = value

        self.session.headers.update(header)
        return self

    def new_request(self):
        return MicaRequest(self)

    def close(self):
        """
        Close client session and request to close Mica server session
        """
        try:
            self.new_request().resource('/auth/session/_current').delete().send()
            self.session.close()
        except Exception as e:
            pass

    class LoginInfo:
        """
        Class used to hold the login info
        """        
        data = None

        @classmethod
        def parse(cls, args):
            """
            Parses the commandline args to extract login relevant info

            :param args - commandline args
            """
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
        self.options = {}
        self.headers = {'Accept': 'application/json'}
        self._verbose = False
        self.params = {}
        self._fail_on_error = False
        self.files = None
        self.data = None

    def timeout(self, value):
        """
        Sets the connection and read timeout
        Note: value can be a tupple to have different timeouts for connection and reading (connTimout, readTimeout)

        :param value - connection/read timout
        """
        if 'timeout' in self.options:
            self.options['timeout'] = (value, self.options['timeout'])
        self.options['timeout'] = value
        return self

    def verbose(self):
        logging.basicConfig(level=logging.DEBUG)
        self._verbose = True
        return self

    def fail_on_error(self):
        self._fail_on_error = True
        return self

    def header(self, key, value):
        if value:
            header = {}
            header[key] = value
            self.headers.update(header)
        return self

    def accept(self, value):
        self.headers.update({'Accept': value})
        return self

    def content_type(self, value):
        self.headers.update({'Content-Type': value})
        return self

    def accept_json(self):
        return self.accept('application/json')

    def content_type_json(self):
        return self.content_type('application/json')

    def content_type_text_plain(self):
        return self.content_type('text/plain')

    def content_type_form(self):
        return self.content_type('application/x-www-form-urlencoded')

    def content_upload(self, filename):
        if self._verbose:
            logging.info('* File Content:')
            logging.info('[file=' + filename + ', size=' + str(os.path.getsize(filename)) + ']')
        self.files = {'file': (filename, open(filename, 'rb'))}
        return self

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

    def resource(self, ws):
        self.resource = ws
        return self

    def query(self, parameters):
      """
      Stores the query parameters
      """
      if isinstance(parameters, tuple):
        param = {}
        param[parameters[0]] = parameters[1]
        self.params.update(param)
      else:
        self.params = parameters

      return self

    def form(self, parameters):
        """
        Stores the request's body as a form
        Note: no need to transform parameters in key=value pairs

        :param parametes - parameters as a dict value
        """
        return self.content(parameters)

    def content(self, content):
        """
        Stores the request body
        """
        if self._verbose:
            print('* Content:')
            print(content)

        self.data = content
        return self

    def __build_request(self):
        """
        Builder method creating a Request object to be sent by the client session object
        """
        request = Request()
        request.method = self.method if self.method else 'GET'

        for option in self.options:
            setattr(request, option, self.options[option])

        # headers
        request.headers = {}
        request.headers.update(self.client.session.headers)
        request.headers.update(self.headers)

        if self.resource:
            path = self.resource
            request.url = self.client.base_url + '/ws' + path

            if self.params:
                request.params = self.params
        else:
            raise ValueError('Resource is missing')

        if self.files is not None:
            request.files = self.files

        if self.data is not None:
            request.data = self.data

        return request


    def send(self):
        """
        Sends the request via client session object
        """
        request = self.__build_request()
        response = MicaResponse(self.client.session.send(request.prepare()))

        if self._fail_on_error and response.code >= 400:
            raise HTTPError(response)

        return response


class MicaResponse:
    """
    Response from Mica: code, headers and content
    """

    def __init__(self, response):
        self.response = response

    @property
    def code(self):
        return self.response.status_code

    @property
    def headers(self):
        return self.response.headers

    @property
    def content(self):
        return self.response.content

    def as_json(self):
        if self.response is None or self.response.content is None:
            return None

        try:
            return self.response.json()
        except Exception as e:
            if type(self.response.content) == str:
                return self.response.content
            else:
              # FIXME silently fail
              return None
    def pretty_json(self):
        return json.dumps(self.as_json(), sort_keys=True, indent=2)


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
        if isinstance(params, tuple):
          self.params = dict((x, y) for x, y in params)
        else:
          self.params = params

        return self

    def query(self, key, value):
        param = {}
        param[key] = value
        self.params.update(param)
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

class MicaService:
  def __init__(self, client: MicaClient,  verbose: bool = False):
    self.client = client
    self.verbose = verbose

  def _make_request(self, fail_safe: bool = False) -> MicaRequest:
    request = self.client.new_request()
    if not fail_safe:
        request.fail_on_error()
    if self.verbose:
        request.verbose(self.verbose)
    return request

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

class Formatter:

    @classmethod
    def to_json(self, data: any, pretty: bool = False):
        if pretty:
            return json.dumps(data, sort_keys=True, indent=2)
        else:
            return json.dumps(data, sort_keys=True)

    @classmethod
    def print_json(self, data: any, pretty: bool = False):
        if data is not None:
            print(self.to_json(data, pretty))