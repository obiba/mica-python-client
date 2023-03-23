import sys
from obiba_mica.core import MicaClient

class RestService:
  """
  Perform raw web services requests.
  """

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  @classmethod
  def add_arguments(cls, parser):
    """
    Add REST command specific options
    """
    parser.add_argument('ws', help='Web service path, for instance: /study/xxx')
    parser.add_argument('--method', '-m', required=False,
                        help='HTTP method (default is GET, others are POST, PUT, DELETE, OPTIONS)')
    parser.add_argument('--accept', '-a', required=False, help='Accept header (default is application/json)')
    parser.add_argument('--content-type', '-ct', required=False,
                        help='Content-Type header (default is application/json)')
    parser.add_argument('--json', '-j', action='store_true', help='Pretty JSON formatting of the response')


  @classmethod
  def do_command(cls, args):
    """
    Execute REST command
    """
    # Build and send request
    client = MicaClient.build(MicaClient.LoginInfo.parse(args))
    service = RestService(client, args.accept, args.verbose)

    # send request
    method = args.method if args.method else 'GET'
    serviceMethod = getattr(service, 'send_%s_request' % method.lower())

    if method in ['POST', 'PUT']:
      response = serviceMethod(args.ws, args.content_type)
    else:
      response = serviceMethod(args.ws)

    # format response
    res = response.content
    if args.json:
      res = response.pretty_json()
    elif args.method in ['OPTIONS']:
      res = response.headers['Allow']

    # output to stdout
    print(res)

  def _make_request(self):
    request = self.client.new_request()
    request.fail_on_error()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def _make_request_with_content_type(self, contentType):
    request = self._make_request()
    if contentType:
      request.content_type(contentType)
      print('Enter content:')
      request.content(sys.stdin.read())

    return request

  def send_get_request(self, url: str):
    request = self._make_request()
    return request.get().resource(url).send()

  def send_options_request(self, url: str):
    request = self._make_request()
    return request.options().resource(url).send()

  def send_delete_request(self, url: str):
    request = self._make_request()
    return request.delete().resource(url).send()

  def send_put_request(self, url: str, contentType):
    request = self._make_request_with_content_type(contentType)
    return request.put().resource(url).send()

  def send_post_request(self, url: str, contentType):
    request = self._make_request_with_content_type(contentType)
    return request.post().resource(url).send()
