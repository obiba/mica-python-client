import sys
from obiba_mica.core import MicaClient


class PluginService:
  """
  Plugins management.
  """
  @classmethod
  def add_arguments(self, parser):
      """
      Add plugin command specific options
      """

      parser.add_argument('--list', '-ls', action='store_true', help='List the installed plugins.')
      parser.add_argument('--updates', '-lu', action='store_true', help='List the installed plugins that can be updated.')
      parser.add_argument('--available', '-la', action='store_true', help='List the new plugins that could be installed.')
      parser.add_argument('--install', '-i', required=False,
                          help='Install a plugin by providing its name or name:version. If no version is specified, the latest version is installed. Requires system restart to be effective.')
      parser.add_argument('--remove', '-rm', required=False,
                          help='Remove a plugin by providing its name. Requires system restart to be effective.')
      parser.add_argument('--reinstate', '-ri', required=False,
                          help='Reinstate a plugin that was previously removed by providing its name.')
      parser.add_argument('--fetch', '-f', required=False, help='Get the named plugin description.')
      parser.add_argument('--configure', '-c', required=False,
                          help='Configure the plugin site properties. Usually requires to restart the associated service to be effective.')
      parser.add_argument('--status', '-su', required=False,
                          help='Get the status of the service associated to the named plugin.')
      parser.add_argument('--start', '-sa', required=False, help='Start the service associated to the named plugin.')
      parser.add_argument('--stop', '-so', required=False, help='Stop the service associated to the named plugin.')
      parser.add_argument('--json', '-j', action='store_true', help='Pretty JSON formatting of the response')


  @classmethod
  def do_command(self, args):
      """
      Execute plugin command
      """
      # Build and send request
      request = core.MicaClient.build(core.MicaClient.LoginInfo.parse(args)).new_request()
      request.fail_on_error().accept_json()

      if args.verbose:
          request.verbose()

      if args.updates:
          response = request.get().resource('/config/plugins/_updates').send()
      elif args.available:
          response = request.get().resource('/config/plugins/_available').send()
      elif args.install:
          nameVersion = args.install.split(':')
          if len(nameVersion) == 1:
              response = request.post().resource('/config/plugins?name=' + nameVersion[0]).send()
          else:
              response = request.post().resource(
                  '/config/plugins?name=' + nameVersion[0] + '&version=' + nameVersion[1]).send()
      elif args.fetch:
          response = request.get().resource('/config/plugin/' + args.fetch).send()
      elif args.configure:
          request.content_type_text_plain()
          print('Enter plugin site properties (one property per line, Ctrl-D to end input):')
          request.content(sys.stdin.read())
          response = request.put().resource('/config/plugin/' + args.configure + '/cfg').send()
      elif args.remove:
          response = request.delete().resource('/config/plugin/' + args.remove).send()
      elif args.reinstate:
          response = request.put().resource('/config/plugin/' + args.reinstate).send()
      elif args.status:
          response = request.get().resource('/config/plugin/' + args.status + '/service').send()
      elif args.start:
          response = request.put().resource('/config/plugin/' + args.start + '/service').send()
      elif args.stop:
          response = request.delete().resource('/config/plugin/' + args.stop + '/service').send()
      else:
          response = request.get().resource('/config/plugins').send()

      # format response
      res = response.content
      if args.json:
          res = response.pretty_json()

      # output to stdout
      print(res)

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