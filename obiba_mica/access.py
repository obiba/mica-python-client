"""
Mica permissions
"""

from obiba_mica.core import UriBuilder, MicaClient

class AccessService:
  """
  Base class for Mica document access management
  """

  SUBJECT_TYPES = ('USER', 'GROUP')

  @classmethod
  def add_permission_arguments(cls, parser, fileArg):
    """
    Add permission arguments
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
    """
    if not args.add and not args.delete and not args.list:
      raise Exception("You must specify an access operation: [--add|-a] or [--delete|-de] or [--list|-ls]")

    if not args.list:
      if not args.subject:
        raise Exception("You must specify a subject, a user or a group")

      if not args.type or args.type.upper() not in AccessService.SUBJECT_TYPES:
        raise Exception("Valid subject types are: %s" % ', '.join(AccessService.SUBJECT_TYPES).lower())

  @classmethod
  def do_ws(cls, args, path):
    """
    Build the web service resource path
    """
    file = 'true'
    if 'no_file' in args and args.no_file:
      file = 'false'

    if args.add:
      return UriBuilder(path) \
        .query('type', args.type.upper()) \
        .query('principal', args.subject) \
        .query('file', file) \
        .build()

    if args.delete:
      return UriBuilder(path) \
        .query('type', args.type.upper()) \
        .query('principal', args.subject) \
        .build()

    if args.list:
      return UriBuilder(path) \
        .build()

  @classmethod
  def getResourcePathParts(cls, resource, args):
     return ['draft', resource, args.id, 'accesses']

  @classmethod
  def get_resource_name(cls):
     pass

  @classmethod
  def do_command_internal(cls, args):
    """
    Execute access command - also used for tests
    """
    # Build and send requests
    cls.validate_args(args)

    request = MicaClient.build(MicaClient.LoginInfo.parse(args)).new_request()

    if args.verbose:
        request.verbose()

    # send request
    if args.delete:
        request.delete()
    elif args.add:
        request.put()
    else:
        request.get()

    try:
        response = request.resource(cls.do_ws(args, cls.getResourcePathParts(cls.get_resource_name(), args))).send()
    except Exception as e:
        print(Exception, e)

    return response

  @classmethod
  def do_command(cls, args):
    response = cls.do_command_internal(args)

    # format response
    if response.code != 204:
        print(response.content)

class ProjectAccessService(AccessService):
  """
  Project access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(ProjectAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Research Project ID')

  @classmethod
  def get_resource_name(cls):
     return 'project'

  @classmethod
  def do_command_internal(cls, args):
      return super(ProjectAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(ProjectAccessService, cls).do_command(args)


class NetworkAccessService(AccessService):
  """
  Network access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(NetworkAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Network ID')

  @classmethod
  def get_resource_name(cls):
     return 'network'

  @classmethod
  def do_command_internal(cls, args):
      return super(NetworkAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      super(NetworkAccessService, cls).do_command(args)

class IndividualStudyAccessService(AccessService):
  """
  Individual Study access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(IndividualStudyAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Individual Study ID')

  @classmethod
  def get_resource_name(cls):
     return 'individual-study'

  @classmethod
  def do_command_internal(cls, args):
      return super(IndividualStudyAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      super(IndividualStudyAccessService, cls).do_command(args)


class HarmonizationInitiativeAccessService(AccessService):
  """
  Harmonization Initiative access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationInitiativeAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Initiative ID')

  @classmethod
  def get_resource_name(cls):
     return 'harmonization-study'

  @classmethod
  def do_command_internal(cls, args):
      return super(HarmonizationInitiativeAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      super(HarmonizationInitiativeAccessService, cls).do_command(args)

class CollectedDatasetAccessService(AccessService):
  """
  Collected Dataset access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(CollectedDatasetAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Collected Dataset ID')

  @classmethod
  def get_resource_name(cls):
     return 'collected-dataset'

  @classmethod
  def do_command_internal(cls, args):
      return super(CollectedDatasetAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(CollectedDatasetAccessService, cls).do_command(args)

class HarmonizationProtocolAccessService(AccessService):
  """
  Harmonization Protocol access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationProtocolAccessService, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Protocol ID')

  @classmethod
  def get_resource_name(cls):
     return 'harmonized-dataset'

  @classmethod
  def do_command_internal(cls, args):
      return super(HarmonizationProtocolAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      super(HarmonizationProtocolAccessService, cls).do_command(args)

class FileAccessService(AccessService):
  """
  file access management
  """

  @classmethod
  def getResourcePathParts(cls, resource, args):
    path = args.path
    while path.startswith('/'):
      path = path[1:]

    return ['draft', resource, path]

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(FileAccessService, cls).add_permission_arguments(parser, False)
      parser.add_argument('path', help='File path in Mica file system')

  @classmethod
  def get_resource_name(cls):
     return 'file-access'

  @classmethod
  def do_command_internal(cls, args):
      return super(FileAccessService, cls).do_command_internal(args)

  @classmethod
  def do_command(cls, args):
      super(FileAccessService, cls).do_command(args)
