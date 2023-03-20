import unittest
from obiba_mica.perm import IndividualStudyPermissionService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    IndividualStudyPermissionService.add_arguments(self.parser)

  def test_addDocumentPermission(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--permission', 'READER', '--add', 'clsa'])
      IndividualStudyPermissionService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_listDocumentPermission(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--list', 'clsa'])
      response = IndividualStudyPermissionService.do_command_internal(args).as_json()
      found = next((x for x in response if x['principal'] == 'user1'), None)

      if found is None:
        assert False

      assert True
    except Exception as e:
      assert False

  def test_removeDocumentPermission(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--delete', 'clsa'])
      IndividualStudyPermissionService.do_command(args)
      assert True
    except Exception as e:
      assert False
