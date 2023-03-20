import unittest
from obiba_mica.access import FileAccessService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    FileAccessService.add_arguments(self.parser)

  def test_addFileAccess(self):
    try:
      self.setup_class()
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--add', '/individual-study/cls/population/1/data-collection-event/4/Wave 4 subject interview.pdf'])
      FileAccessService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_listDocumentAccess(self):
    try:
      self.setup_class()
      args = Utils.parse_arg_values(parser=self.parser,params=['--list', '/individual-study/cls/population/1/data-collection-event/4/Wave 4 subject interview.pdf'])
      response = FileAccessService.do_command_internal(args).as_json()
      found = next((x for x in response if x['principal'] == 'user1'), None)

      if found is None:
        assert False

      assert True
    except Exception as e:
      assert False

  def test_removeRemoveAccess(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--type', 'USER', '--subject', 'user1', '--delete', '/individual-study/cls/population/1/data-collection-event/4/Wave 4 subject interview.pdf'])
      FileAccessService.do_command(args)
      assert True
    except Exception as e:
      assert False
