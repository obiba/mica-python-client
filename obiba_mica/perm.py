"""
Mica permissions
"""

from obiba_mica.core import UriBuilder, MicaClient

class PermissionService:
  SUBJECT_TYPES = ('USER', 'GROUP')
  PERMISSIONS = ('READER', 'EDITOR', 'REVIEWER')

  @classmethod
  def add_permission_arguments(cls, parser):
    """
    Add permission arguments
    """
    parser.add_argument('--add', '-a', action='store_true', help='Add a permission')
    parser.add_argument('--delete', '-d', action='store_true', required=False, help='Delete a permission')
    parser.add_argument('--permission', '-pe', help="Permission to apply: %s" % ', '.join(PermissionService.PERMISSIONS).lower())
    parser.add_argument('--subject', '-s', required=True, help='Subject name to which the permission will be granted')
    parser.add_argument('--type', '-ty', required=False, help='Subject type: user or group')

  @classmethod
  def map_permission(cls, permission):
    """
    Map permission argument to permission query parameter
    """
    if permission.upper() not in PermissionService.PERMISSIONS:
      return None

    return permission.upper()

  @classmethod
  def validate_args(cls, args):
    """
    Validate action, permission and subject type
    """
    if not args.add and not args.delete:
      raise Exception("You must specify a permission operation: [--add|-a] or [--delete|-de]")

    if args.add:
      if not args.permission:
        raise Exception("A permission name is required: %s" % ', '.join(PermissionService.PERMISSIONS).lower())
      if cls.map_permission(args.permission) is None:
        raise Exception("Valid permissions are: %s" % ', '.join(PermissionService.PERMISSIONS).lower())

    if not args.type or args.type.upper() not in PermissionService.SUBJECT_TYPES:
      raise Exception("Valid subject types are: %s" % ', '.join(PermissionService.SUBJECT_TYPES).lower())

  @classmethod
  def do_ws(cls, args, path):
    """
    Build the web service resource path
    """
    if args.add:
      return UriBuilder(path) \
        .query('type', args.type.upper()) \
        .query('role', cls.map_permission(args.permission)) \
        .query('principal', args.subject) \
        .build()

    if args.delete:
      return UriBuilder(path) \
        .query('type', args.type.upper()) \
        .query('principal', args.subject) \
        .build()

  @classmethod
  def getResourcePathParts(cls, resource, args):
     return ['draft', resource, args.id, 'permissions']

  @classmethod
  def do_command(cls, resource, args):
      """
      Execute permission command
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

      response = request.resource(cls.do_ws(args, cls.getResourcePathParts(resource, args))).send()

      # format response
      if response.code != 204:
          print(response.content)


class ProjectPermissionService(PermissionService):
  """
  Apply permissions on a research project.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(ProjectPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Research Project ID')

  @classmethod
  def do_command(cls, args):
    super(ProjectPermissionService, cls).do_command('project', args)

class NetworkPermissionService(PermissionService):
  """
  Apply permissions on a network.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(NetworkPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Network ID')

  @classmethod
  def do_command(cls, args):
    super(NetworkPermissionService, cls).do_command('network', args)

class IndividualStudyPermissionService(PermissionService):
  """
  Apply permissions on a individual study.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(IndividualStudyPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Individual Study ID')

  @classmethod
  def do_command(cls, args):
    super(IndividualStudyPermissionService, cls).do_command('individual-study', args)


class HarmonizationInitiativePermissionService(PermissionService):
  """
  Apply permissions on a harmonization initiative.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationInitiativePermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Harmonization Initiative ID')

  @classmethod
  def do_command(cls, args):
    super(HarmonizationInitiativePermissionService, cls).do_command('harmonization-study', args)

class HarmonizationProtocolPermissionService(PermissionService):
  """
  Apply permissions on a harmonization protocol.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(HarmonizationProtocolPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Harmonization Protocol ID')

  @classmethod
  def do_command(cls, args):
    super(HarmonizationProtocolPermissionService, cls).do_command('harmonized-dataset', args)

class CollectedDatasetPermissionService(PermissionService):
  """
  Apply permissions on a collected dataset.
  """

  @classmethod
  def add_arguments(cls, parser):
      """
      Add command specific options
      """
      super(CollectedDatasetPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Collected Dataset ID')

  @classmethod
  def do_command(cls, args):
    super(CollectedDatasetPermissionService, cls).do_command('collected-dataset', args)
