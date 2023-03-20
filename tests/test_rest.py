import unittest
from obiba_mica.rest import RestService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    RestService.add_arguments(self.parser)

  def test_validRestCall(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['/draft/individual-studies'])
      RestService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_invalidRestCall(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['/draft/individual-studies'])
      RestService.do_command(args)
      assert False
    except Exception as e:
      assert True
