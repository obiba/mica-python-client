import unittest
from obiba_mica.plugin import PluginService
from tests.utils import Utils

class TestClass(unittest.TestCase):
  __test__ = False # This test needs Mica to restart for each action, only useful for manual and controlled tests


  @classmethod
  def setup_class(cls):
    cls.service = PluginService(Utils.make_client())

  def test_addSearchPlugin(self):
    try:
      response = self.service.install('mica-search-es')
      assert response.code == 200
    except Exception as e:
      assert False

  def test_removeSearchPlugin(self):
    try:
      response = self.service.remove('mica-search-es')
      assert response.code == 204
    except Exception as e:
      assert False

  def test_updateSearchPluginConfig(self):
    try:
      self.service.configure('mica-search-es')
      assert True
    except Exception as e:
      assert False

  def test_listPlugins(self):
    try:
      response = self.service.list()
      assert response.code == 200
    except Exception as e:
      assert False
