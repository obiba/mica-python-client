"""
Mica permissions
"""

from obiba_mica.core import UriBuilder, MicaClient

class AccessService:
  """
  Base class for Mica document access management
  """

  SUBJECT_TYPES = ('USER', 'GROUP')

  def __init__(self, client, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def _get_resource_path(self, id: str):
     """
     Returns the Mica document (Network, Initiativem Study, etc) resource path

     :param id - document id
     """
     pass

  def __make_request(self):
    request = self.client.new_request()
    request.fail_on_error()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def add_access(self, id, type: str, subject: str, noFile: bool = True):
    """
    Adds access to a user or group

    :param id - document id
    :param subject - associated user/group
    :param noFile - exclude access to document's files
    """
    uri = UriBuilder(self._get_resource_path(id)) \
      .query('type', type.upper()) \
      .query('principal', subject) \
      .query('file', str(noFile).lower()) \
      .build()

    return self.__make_request().resource(uri).put().send()

  def delete_access(self, id, type: str, subject: str):
    """
    Removes access from a user or group

    :param id - document id
    :param subject - associated user/group
    """
    uri = UriBuilder(self._get_resource_path(id)) \
      .query('type', type.upper()) \
      .query('principal', subject) \
      .build()

    return self.__make_request().resource(uri).delete().send()

  def list_accesses(self, id):
    """
    Lists all associated accesses of a Mica document

    :param id - document id
    """
    uri = UriBuilder(self._get_resource_path(id)).build()

    return self.__make_request().resource(uri).get().send()

  @classmethod
  def add_permission_arguments(cls, parser, fileArg):
    """
    Add permission arguments

    :param parser - commandline args parser
    :param fileArg - If True, 'noFile' commandline arg is added
    """
    parser.add_argument('--add', '-a', action='store_true', help='Grant an access right')
    parser.add_argument('--delete', '-d', action='store_true', required=False, help='Delete an access right')
    parser.add_argument('--list', '-ls', action='store_true', required=False, help='List access rights')
    if fileArg:
      parser.add_argument('--no-file', '-nf', action='store_true', help='Do not apply the access to the associated files')
    parser.add_argument('--subject', '-s', required=False, help='Subject name to which the access will be granted. Use wildcard * to specify anyone or any group')
    parser.add_argument('--type', '-ty', required=False, help='Subject type: user or group')

  @classmethod
  def validate_args(cls, args):
    """
    Validate action, permission and subject type

    :param args - commandline args
    """
    if not args.add and not args.delete and not args.list:
      raise Exception("You must specify an access operation: [--add|-a] or [--delete|-de] or [--list|-ls]")

    if not args.list:
      if not args.subject:
        raise Exception("You must specify a subject, a user or a group")

      if not args.type or args.type.upper() not in AccessService.SUBJECT_TYPES:
        raise Exception("Valid subject types are: %s" % ', '.join(AccessService.SUBJECT_TYPES).lower())

  @classmethod
  def do_command(cls, args):
    """
    Execute access command - also used for tests

    :param args - commandline args
    """
    # Build and send requests
    cls.validate_args(args)
    service = cls(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)

    try:

      if args.delete:
        response = service.delete_access(args.id, args.type, args.subject)
      elif args.add:
        response = service.add_access(args.id, args.type, args.subject, 'no_file' not in args or not args.no_file)
      else:
        response = service.list_accesses(args.id)

      if response.code != 204:
          print(response.as_json())

    except Exception as e:
        print(Exception, e)


class ProjectAccessService(AccessService):
  """
  Project access management
  """

  @classmethod
  def add_arguments(cls, parser):
    super(ProjectAccessService, cls).add_permission_arguments(parser, True)
    parser.add_argument('id', help='Research Project ID')

  def _get_resource_path(self, id: str):
     return ['draft', 'project', id, 'accesses']

  @classmethod
  def do_command(cls, args):
      super(ProjectAccessService, cls).do_command(args)


class NetworkAccessService(AccessService):
  """
  Network access management
  """

  @classmethod
  def add_arguments(cls, parser):
    super(NetworkAccessService, cls).add_permission_arguments(parser, True)
    parser.add_argument('id', help='Network ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'network', id, 'accesses']

  @classmethod
  def do_command(cls, args):
    super(NetworkAccessService, cls).do_command(args)

class IndividualStudyAccessService(AccessService):
  """
  Individual Study access management
  """

  @classmethod
  def add_arguments(cls, parser):
    super(IndividualStudyAccessService, cls).add_permission_arguments(parser, True)
    parser.add_argument('id', help='Individual Study ID')

  def _get_resource_path(self, id: str):
     return ['draft', 'individual-study', id, 'accesses']

  @classmethod
  def do_command(cls, args):
      super(IndividualStudyAccessService, cls).do_command(args)


class HarmonizationInitiativeAccessService(AccessService):
  """
  Harmonization Initiative access management
  """

  @classmethod
  def add_arguments(cls, parser):
      super(HarmonizationInitiativeAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Initiative ID')

  def _get_resource_path(self, id: str):
     return ['draft', 'harmonization-study', id, 'accesses']

  @classmethod
  def do_command(cls, args):
      super(HarmonizationInitiativeAccessService, cls).do_command(args)

class CollectedDatasetAccessService(AccessService):
  """
  Collected Dataset access management
  """

  @classmethod
  def add_arguments(cls, parser):
      super(CollectedDatasetAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Collected Dataset ID')

  def _get_resource_path(self, id: str):
     return ['draft', 'collected-dataset', id, 'accesses']

  @classmethod
  def do_command(cls, args):
      super(CollectedDatasetAccessService, cls).do_command(args)

class HarmonizationProtocolAccessService(AccessService):
  """
  Harmonization Protocol access management
  """

  @classmethod
  def add_arguments(cls, parser):
      super(HarmonizationProtocolAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Protocol ID')

  def _get_resource_path(self, id: str):
     return ['draft', 'harmonized-dataset', id, 'accesses']

  @classmethod
  def do_command(cls, args):
      super(HarmonizationProtocolAccessService, cls).do_command(args)

class FileAccessService(AccessService):
  """
  file access management
  """

  def _get_resource_path(self, id: str):
    path = id
    while path.startswith('/'):
      path = path[1:]

    return ['draft', 'file-access', path]

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(FileAccessService, cls).add_permission_arguments(parser, False)
      parser.add_argument('id', help='File path in Mica file system')

  @classmethod
  def get_resource_name(cls):
     return 'file-access'

  @classmethod
  def do_command(cls, args):
      super(FileAccessService, cls).do_command(args)
