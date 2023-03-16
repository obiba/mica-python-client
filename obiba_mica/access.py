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
    if fileArg:
      parser.add_argument('--no-file', '-nf', action='store_true', help='Do not apply the access to the associated files')
    parser.add_argument('--subject', '-s', required=True, help='Subject name to which the access will be granted. Use wildcard * to specify anyone or any group')
    parser.add_argument('--type', '-ty', required=False, help='Subject type: user or group')

  @classmethod
  def validate_args(cls, args):
    """
    Validate action, permission and subject type
    """
    if not args.add and not args.delete:
      raise Exception("You must specify an access operation: [--add|-a] or [--delete|-de]")

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

  @classmethod
  def getResourcePathParts(cls, resource, args):
     return ['draft', resource, args.id, 'accesses']

  @classmethod
  def do_command(cls, resource, args):
      """
      Execute access command
      """
      # Build and send requests
      cls.validate_args(args)

      request = MicaClient.build(MicaClient.LoginInfo.parse(args)).new_request()

      if args.verbose:
          request.verbose()

      # send request
      if args.delete:
          request.delete()
      else:
          request.put()

      try:
          response = request.resource(cls.do_ws(args, cls.getResourcePathParts(resource, args))).send()
      except Exception as e:
          print(Exception, e)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(ProjectAccessService, cls).do_command('project', args)


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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(NetworkAccessService, cls).do_command('network', args)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(IndividualStudyAccessService, cls).do_command('individual-study', args)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(HarmonizationInitiativeAccessService, cls).do_command('harmonization-study', args)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(CollectedDatasetAccessService, cls).do_command('collected-dataset', args)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(HarmonizationProtocolAccessService, cls).do_command('harmonized-dataset', args)

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
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(FileAccessService, cls).do_command('file-access', args)
