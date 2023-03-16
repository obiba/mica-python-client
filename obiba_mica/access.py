"""
Mica permissions
"""

from obiba_mica.core import UriBuilder, MicaClient

class Access:
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

    if not args.type or args.type.upper() not in Access.SUBJECT_TYPES:
      raise Exception("Valid subject types are: %s" % ', '.join(Access.SUBJECT_TYPES).lower())

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

class ProjectAccess(Access):
  """
  Project access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(ProjectAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Research Project ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(ProjectAccess, cls).do_command('project', args)


class NetworkAccess(Access):
  """
  Network access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(NetworkAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Network ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(NetworkAccess, cls).do_command('network', args)

class IndividualStudyAccess(Access):
  """
  Individual Study access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(IndividualStudyAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Individual Study ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(IndividualStudyAccess, cls).do_command('individual-study', args)

class HarmonizationInitiativeAccess(Access):
  """
  Harmonization Initiative access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationInitiativeAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Initiative ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(HarmonizationInitiativeAccess, cls).do_command('harmonization-study', args)

class CollectedDatasetAccess(Access):
  """
  Collected Dataset access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(CollectedDatasetAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Collected Dataset ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(CollectedDatasetAccess, cls).do_command('collected-dataset', args)

class HarmonizationProtocolAccess(Access):
  """
  Harmonization Protocol access management
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationProtocolAccess, cls).add_permission_arguments(parser, True)
      parser.add_argument('id', help='Harmonization Protocol ID')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(HarmonizationProtocolAccess, cls).do_command('harmonized-dataset', args)

class FileAccess(Access):
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
      super(FileAccess, cls).add_permission_arguments(parser, False)
      parser.add_argument('path', help='File path in Mica file system')

  @classmethod
  def do_command(cls, args):
      """
      Execute access command
      """
      # Build and send requests
      super(FileAccess, cls).do_command('file-access', args)
