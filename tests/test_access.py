import unittest
from obiba_mica.access import IndividualStudyAccessService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    IndividualStudyAccessService.add_arguments(self.parser)

  def test_addDocumentAccess(self):
    try:
      self.setup_class()
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--add', 'clsa'])
      IndividualStudyAccessService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_listDocumentAccess(self):
    try:
      self.setup_class()
      args = Utils.parse_arg_values(parser=self.parser,params=['--list', 'clsa'])
      response = IndividualStudyAccessService.do_command_internal(args).as_json()
      found = next((x for x in response if x['principal'] == 'user1'), None)

      if found is None:
        assert False
        
      assert True
    except Exception as e:
      assert False

  def test_removeDocumentAccess(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--delete', 'clsa'])
      IndividualStudyAccessService.do_command(args)
      assert True
    except Exception as e:
      assert False
