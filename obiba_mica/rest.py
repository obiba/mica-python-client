import sys
import ast
from obiba_mica.core import MicaClient
from obiba_mica.core import MicaRequest

class RestService:
  """
  Perform raw web services requests.
  """

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def make_request(self, method: str):
    """
    Creates a MicaRequest instance

    Note: all responses are return in JSON form

    :param method - HTTP method
    """
    request = self.client.new_request()
    request.method(method)
    request.fail_on_error()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def make_request_with_content_type(self, method: str, contentType: str, content: str = None):
    """
    Creates a MicaRequest instance with a request body

    :param method - HTTP method
    :param contentType - request content type
    :param content - data to be posted (if ignored a prompt will read-in data from commandline ending with a CTRL-D)
    """
    request = self.make_request(method)
    if contentType:
      request.content_type(contentType)

      if content is not None:
          request.content(content.encode('utf-8'))
      else:
        print('Enter content:')
        request.content(str(sys.stdin.read()).encode('utf-8'))

    return request

  def send_request(self, url: str, request: MicaRequest):
    """
    Sends the request to Mica server
    """
    return request.resource(url).send()


  @classmethod
  def add_arguments(cls, parser):
    """
    Add REST command specific options

    :param parser - commandline args parser
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

    :param args - commandline args
    """
    # Build and send request
    client = MicaClient.build(MicaClient.LoginInfo.parse(args))

    try:
        request = client.new_request()
        request.fail_on_error()

        if args.accept:
            request.accept(args.accept)
        else:
            request.accept_json()

        if args.content_type:
            request.content_type(args.content_type)
            print('Enter content:')
            request.content(str(sys.stdin.read()).encode('utf-8'))

        if args.verbose:
            request.verbose()

        # send request
        request.method(args.method).resource(args.ws)
        response = request.send()

        # format response
        res = response.as_json()
        if args.json:
            res = response.pretty_json()
        elif args.method in ['OPTIONS']:
            res = response.headers['Allow']

        # output to stdout
        print(res)
    finally:
        client.close()
