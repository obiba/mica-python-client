import unittest
from obiba_mica.file import FileService
from tests.utils import Utils
import json

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = FileService(Utils.make_client())

  def test_1_fileUpload(self):
    try:
      response = self.service.upload('/individual-study',  './tests/resources/dummy.csv')

      if response.code == 201:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def __test_fileChangeStatus(self, file, status):
    try:
      response = self.service.status(file, status)

      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def __test_fileDelete(self, path):
    try:
      response = self.service.delete(path)

      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_2_fileUnderReviewStatus(self):
    self.__test_fileChangeStatus('/individual-study/dummy.csv', FileService.STATUS_UNDER_REVIEW)

  def test_3_filePublish(self):
    try:
      response = self.service.publish('/individual-study/dummy.csv', True)

      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_4_fileJson(self):
    try:
      response = self.service.get('/individual-study/dummy.csv')

      if response is None:
        assert False
      else:
        parsed = json.loads(response.content)
        if parsed['name'] != 'dummy.csv' and parsed['state']['publishedId'] == None:
          assert False

      assert True
    except Exception as e:
      assert False

  def test_5_fileDownload(self):
    try:
      response = self.service.download('/individual-study/dummy.csv')

      if response is None or 'col1' not in response.content.decode('utf-8'):
        assert False

      assert True
    except Exception as e:
      assert False

  def test_6_changeDeletedStatus(self):
    self.__test_fileChangeStatus('/individual-study/dummy.csv', FileService.STATUS_DELETED)

  def test_7_fileDelete(self):
    self.__test_fileDelete('/individual-study/dummy.csv')

  def test_8_createFolder(self):
    try:
      response = self.service.create("/individual-study", "yoyo")

      if response.code == 201:
        self.__test_fileChangeStatus('/individual-study/yoyo', FileService.STATUS_DELETED)
        self.__test_fileDelete('/individual-study/yoyo')

      else:
        assert False

    except Exception as e:
      assert False



