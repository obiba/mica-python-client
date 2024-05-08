import unittest
from obiba_mica.import_zip import FileImportService
from obiba_mica.rest import RestService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.client = Utils.make_client()

  def __test_changeResourceStatusToDelete(self, restService, resource):
    try:
      response = restService.send_request('%s/_status?value=DELETED' % resource, restService.make_request('PUT'))

      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def __test_deleteResource(self, restService, resource):
    try:
      response = restService.send_request(resource, restService.make_request('DELETE'))

      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_1_importZip(self):
    try:
      service = FileImportService(self.client)
      response = service.import_zip('./tests/resources/dummy-test-study.zip', True, False)
      assert response.code == 200
    except Exception as e:
      assert False

  def test_2_deleteDummy(self):
    try:
      restService = RestService(self.client)
      self.__test_changeResourceStatusToDelete(restService, '/draft/network/dummy-test-network')
      self.__test_deleteResource(restService, '/draft/network/dummy-test-network')
      self.__test_changeResourceStatusToDelete(restService, '/draft/individual-study/dummy-test-study')
      self.__test_deleteResource(restService, '/draft/individual-study/dummy-test-study')
    except Exception as e:
      assert False


  def test_3_importZip(self):
    try:
      service = FileImportService(self.client)
      response = service.import_zip('./tests/resources/dummy-test-study-legacy.zip', True, True)
      assert response.code == 200
    except Exception as e:
      assert False

  def test_4_deleteDummy(self):
    try:
      restService = RestService(self.client)
      self.__test_changeResourceStatusToDelete(restService, '/draft/network/dummy-test-network')
      self.__test_deleteResource(restService, '/draft/network/dummy-test-network')
      self.__test_changeResourceStatusToDelete(restService, '/draft/individual-study/dummy-test-study')
      self.__test_deleteResource(restService, '/draft/individual-study/dummy-test-study')
    except Exception as e:
      assert False


