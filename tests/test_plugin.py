import unittest
from obiba_mica.plugin import PluginService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    PluginService.add_arguments(self.parser)

  def test_addSearchPlugin(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--install', 'mica-search-es'])
      PluginService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_removeSearchPlugin(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--remove', 'mica-search-es'])
      PluginService.do_command(args)
      assert True
    except Exception as e:
      assert False

  def test_listPlugins(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--list'])
      PluginService.do_command(args)
      assert True
    except Exception as e:
      assert False
