import sys
from obiba_mica.core import MicaClient, MicaRequest

class PluginService:
  """
  Mica plugin management.
  """

  def __init__(self, client, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def __make_request(self) -> MicaRequest:
    request = self.client.new_request()
    request.fail_on_error()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def updates(self):
    """
    Returns a list of plugin updates
    """
    return self.__make_request().resource('/config/plugins/_updates').get().send()

  def available(self):
    """
    Returns a list of available plugins
    """
    return self.__make_request().resource('/config/plugins/_available').get().send()

  def fetch(self, name: str):
    """
    Retrieves a plugin

    :param name - plugin name
    """
    return self.__make_request().resource('/config/plugin/%s' % name).get().send()

  def install(self, nameVersion: str):
    """
    Installs a plugin by name and version

    :param nameVersion - name and versoin separated by a colon (name:version)
    """

    parts = nameVersion.split(':')
    if len(parts) == 1:
      url = '/config/plugins?name=%s' % parts[0]
    else:
      url = '/config/plugins?name=%s$%d' % (parts[0], parts[1])

    return self.__make_request().resource(url).post().send()

  def configure(self, configure: str):
    """
    Adds configuration properties to a plugin

    Example:

    :param configure - plugin name
    """
    request = self.__make_request().content_type_text_plain()
    print('Enter plugin site properties (one property per line, Ctrl-D to end input):')
    request.content(sys.stdin.read())
    return request.put().resource('/config/plugin/%s/cfg' % configure).send()

  def remove(self, nameVersion: str):
    """
    Removes a plugin by name and version

    :param nameVersion - name and versoin separated by a colon (name:version)
    """
    return self.__make_request().resource('/config/plugin/%s' % nameVersion).delete().send()

  def reinstate(self, name: str):
    """
    Reinstates/cancel a plugin uninstalation

    :param name - plugin name
    """
    return self.__make_request().resource('/config/plugin/%s' % name).put().send()

  def status(self, name: str):
    """
    Returns the status of the plugin

    :param name - plugin name
    """
    return self.__make_request().resource('/config/plugin/%s/service' % name).get().send()

  def start(self, name: str):
    """
    Starts a plugin

    :param name - plugin name
    """
    return self.__make_request().resource('/config/plugin/%s/service' % name).put().send()

  def stop(self, name: str):
    """
    Stops a plugin

    :param name - plugin name
    """
    return self.__make_request().resource('/config/plugin/%s/service' % name).delete().send()

  def list(self):
    """
    Lists the installed plugins
    """
    return self.__make_request().resource('/config/plugins').get().send()

  @classmethod
  def add_arguments(cls, parser):
      """
      Add plugin command specific options

      :param parser - commandline args parser
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
  def do_command(cls, args):
      """
      Execute plugin command

      :param args - commandline args
      """
      # Build and send request
      client = MicaClient.build(MicaClient.LoginInfo.parse(args))
      service = PluginService(client, args.verbose)

      if args.updates:
          response = service.updates()
      elif args.available:
          response = service.available()
      elif args.install:
          service.install(args.install)
      elif args.fetch:
          response = service.fetch(args.fetch)
      elif args.configure:
          response = service.configure(args.configure)
      elif args.remove:
          response = service.remove(args.remove)
      elif args.reinstate:
          response = service.reinstate(args.reinstate)
      elif args.status:
          response = service.status(args.status)
      elif args.start:
          response = service.start(args.start)
      elif args.stop:
          response = service.stop(args.stop)
      else:
          response = service.list()

      # format response
      res = response.content
      if args.json:
          res = response.as_json()

      # output to stdout
      print(res)
