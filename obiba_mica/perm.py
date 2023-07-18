"""
Mica permissions
"""

from obiba_mica.core import UriBuilder, MicaClient

class PermissionService:
  """
  Base class for Mica document permission management
  """

  SUBJECT_TYPES = ('USER', 'GROUP')
  PERMISSIONS = ('READER', 'EDITOR', 'REVIEWER')

  def __init__(self, client, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def _get_resource_path(self, id: str):
     pass

  def __make_request(self):
    request = self.client.new_request()
    request.fail_on_error()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def add_permission(self, id, type: str, subject: str, permission: str):
    """
    Adds a user/group permission to a Mica document

    :param id - document id
    :param subject - associated user/group
    :param permission - 'READER', 'EDITOR', 'REVIEWER'
    """
    uri = UriBuilder(self._get_resource_path(id)) \
      .query('type', type.upper()) \
      .query('role', self.map_permission(permission)) \
      .query('principal', subject) \
      .build()

    return self.__make_request().resource(uri).put().send()

  def delete_permission(self, id, type: str, subject: str):
    """
    Removes a user/group permission from a Mica document

    :param id - document id
    :param subject - associated user/group
    """
    uri = UriBuilder(self._get_resource_path(id)) \
      .query('type', type.upper()) \
      .query('principal', subject) \
      .build()

    return self.__make_request().resource(uri).delete().send()

  def list_permissions(self, id):
    """
    Lists all persmissions given to a Mica document

    :param id - document id
    """
    uri = UriBuilder(self._get_resource_path(id)).build()

    return self.__make_request().resource(uri).get().send()

  @classmethod
  def add_permission_arguments(cls, parser):
    """
    Add permission arguments

    :param parser - commandline args parser
    """
    parser.add_argument('--add', '-a', action='store_true', help='Add a permission')
    parser.add_argument('--delete', '-d', action='store_true', required=False, help='Delete a permission')
    parser.add_argument('--list', '-ls', action='store_true', required=False, help='List permissions')
    parser.add_argument('--permission', '-pe', help="Permission to apply: %s" % ', '.join(PermissionService.PERMISSIONS).lower())
    parser.add_argument('--subject', '-s', required=False, help='Subject name to which the permission will be granted')
    parser.add_argument('--type', '-ty', required=False, help='Subject type: user or group')

  @classmethod
  def map_permission(cls, permission):
    """
    Map permission argument to permission query parameter

    :param permission - permission name as a string
    """
    if permission.upper() not in PermissionService.PERMISSIONS:
      return None

    return permission.upper()

  @classmethod
  def validate_args(cls, args):
    """
    Validate action, permission and subject type

    :param args - commandline args
    """
    if not args.add and not args.delete and not args.list:
      raise Exception("You must specify a permission operation: [--add|-a] or [--delete|-de]")

    if args.add:
      if not args.permission:
        raise Exception("A permission name is required: %s" % ', '.join(PermissionService.PERMISSIONS).lower())
      if cls.map_permission(args.permission) is None:
        raise Exception("Valid permissions are: %s" % ', '.join(PermissionService.PERMISSIONS).lower())

    if not args.list:
      if not args.subject:
        raise Exception("You must specify a subject, a user or a group")

      if not args.type or args.type.upper() not in PermissionService.SUBJECT_TYPES:
        raise Exception("Valid subject types are: %s" % ', '.join(PermissionService.SUBJECT_TYPES).lower())

  @classmethod
  def do_command(cls, args):
    """
    Execute permission command

    :param args - commandline args
    """
    # Build and send requests
    cls.validate_args(args)

    service = cls(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)

    try:

      if args.delete:
        response = service.delete_permission(args.id, args.type, args.subject)
      elif args.add:
        response = service.add_permission(args.id, args.type, args.subject, args.permission)
      else:
        response = service.list_permissions(args.id)

      # format response
      if response.code != 204:
          print(response.as_json())

    except Exception as e:
      print(Exception, e)

class ProjectPermissionService(PermissionService):
  """
  Apply permissions on a research project.
  """

  @classmethod
  def add_arguments(cls, parser):
    super(ProjectPermissionService, cls).add_permission_arguments(parser)
    parser.add_argument('id', help='Research Project ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'project', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    super(ProjectPermissionService, cls).do_command(args)

class NetworkPermissionService(PermissionService):
  """
  Apply permissions on a network.
  """

  @classmethod
  def add_arguments(cls, parser):
      super(NetworkPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Network ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'network', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    super(NetworkPermissionService, cls).do_command(args)

class IndividualStudyPermissionService(PermissionService):
  """
  Apply permissions on a individual study.
  """

  @classmethod
  def add_arguments(cls, parser):
    super(IndividualStudyPermissionService, cls).add_permission_arguments(parser)
    parser.add_argument('id', help='Individual Study ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'individual-study', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    return super(IndividualStudyPermissionService, cls).do_command(args)

class HarmonizationInitiativePermissionService(PermissionService):
  """
  Apply permissions on a harmonization initiative.
  """

  @classmethod
  def add_arguments(cls, parser):
    super(HarmonizationInitiativePermissionService, cls).add_permission_arguments(parser)
    parser.add_argument('id', help='Harmonization Initiative ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'harmonization-study', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    super(HarmonizationInitiativePermissionService, cls).do_command(args)

class HarmonizationProtocolPermissionService(PermissionService):
  """
  Apply permissions on a harmonization protocol.
  """

  @classmethod
  def add_arguments(cls, parser):
      super(HarmonizationProtocolPermissionService, cls).add_permission_arguments(parser)
      parser.add_argument('id', help='Harmonization Protocol ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'harmonized-dataset', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    super(HarmonizationProtocolPermissionService, cls).do_command(args)

class CollectedDatasetPermissionService(PermissionService):
  """
  Apply permissions on a collected dataset.
  """

  @classmethod
  def add_arguments(cls, parser):
    super(CollectedDatasetPermissionService, cls).add_permission_arguments(parser)
    parser.add_argument('id', help='Collected Dataset ID')

  def _get_resource_path(self, id: str):
    return ['draft', 'collected-dataset', id, 'permissions']

  @classmethod
  def do_command(cls, args):
    super(CollectedDatasetPermissionService, cls).do_command(args)
