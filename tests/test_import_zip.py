import unittest
from obiba_mica.import_zip import FileImportService
from obiba_mica.rest import RestService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.service = FileImportService(Utils.make_client())

  def test_importZip(self):
    try:
      response = self.service.import_zip('./tests/resources/dummy-test-study.zip', True)
      assert response.code == 200
    except Exception as e:
      assert False


