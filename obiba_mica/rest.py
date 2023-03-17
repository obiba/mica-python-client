import sys
from obiba_mica.core import MicaClient

class RestService:
  """
  Perform raw web services requests.
  """

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
    request = MicaClient.build(MicaClient.LoginInfo.parse(args)).new_request()
    request.fail_on_error()

    if args.accept:
        request.accept(args.accept)
    else:
        request.accept_json()

    if args.content_type:
        request.content_type(args.content_type)
        print('Enter content:')
        request.content(sys.stdin.read())

    if args.verbose:
        request.verbose()

    # send request
    request.method(args.method).resource(args.ws)
    response = request.send()

    # format response
    res = response.content
    if args.json:
        res = response.pretty_json()
    elif args.method in ['OPTIONS']:
        res = response.headers['Allow']

    # output to stdout
    print(res)