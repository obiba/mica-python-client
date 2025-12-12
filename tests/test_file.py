import unittest
from obiba_mica.file import FileService
from tests.utils import Utils
import json

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = FileService(Utils.make_client())
    # Clean up any leftover file from previous test runs
    cls._cleanup_test_file()

  @classmethod
  def teardown_class(cls):
    # Clean up after all tests complete
    cls._cleanup_test_file()

  @classmethod
  def _cleanup_test_file(cls):
    """Clean up test file to ensure test isolation"""
    from obiba_mica.core import HTTPError
    try:
      existing = cls.service.get('/individual-study/dummy.csv')
      if existing:
        current_status = existing.as_json().get('revisionStatus')
        if current_status != FileService.STATUS_DELETED:
          try:
            cls.service.status('/individual-study/dummy.csv', FileService.STATUS_DELETED)
          except Exception:
            pass
        try:
          cls.service.delete('/individual-study/dummy.csv')
        except Exception:
          pass
    except HTTPError:
      pass  # File doesn't exist, which is fine

  def test_1_fileUpload(self):
    try:
      response = self.service.upload('/individual-study',  './tests/resources/dummy.csv')

      if response.code == 201:
        # Wait for file to be indexed/available after upload
        Utils.wait_for_condition(
          lambda: self.service.get('/individual-study/dummy.csv') is not None,
          timeout=Utils.get_timeout(10)
        )
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def __test_fileChangeStatus(self, file, status):
    from obiba_mica.core import HTTPError

    def try_status_change():
      try:
        response = self.service.status(file, status)
        return response.code == 204
      except HTTPError as e:
        # Retry on 404 (file not indexed yet) or 5xx (server errors)
        if e.code == 404 or e.is_server_error():
          return False
        raise

    # Retry with exponential backoff - longer timeout in CI
    timeout = Utils.get_timeout(7)  # 7s local, 21s in CI
    success = Utils.wait_for_condition(try_status_change, timeout=timeout, interval=1, backoff='exponential')
    assert success, f"Failed to change status to {status} for {file}"

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
        # Wait for publish to complete/propagate
        Utils.wait_for_condition(
          lambda: self.service.get('/individual-study/dummy.csv') is not None,
          timeout=Utils.get_timeout(10)
        )
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

    # Wait for status change to propagate before test_7 tries to delete
    def check_status():
      try:
        state = self.service.get('/individual-study/dummy.csv').as_json()
        return state.get('revisionStatus') == FileService.STATUS_DELETED
      except Exception:
        return False

    assert Utils.wait_for_condition(check_status, timeout=Utils.get_timeout(10)), \
        "File status did not propagate to DELETED"

  def test_7_fileDelete(self):
    self.__test_fileDelete('/individual-study/dummy.csv')

  def test_8_createFolder(self):
    try:
      response = self.service.create("/individual-study", "yoyo")

      if response.code == 201:
        self.__test_fileChangeStatus('/individual-study/yoyo', FileService.STATUS_DELETED)

        # Wait for status change to propagate before delete
        def check_status():
          try:
            state = self.service.get('/individual-study/yoyo').as_json()
            return state.get('revisionStatus') == FileService.STATUS_DELETED
          except Exception:
            return False

        assert Utils.wait_for_condition(check_status, timeout=Utils.get_timeout(10)), \
            "Folder status did not propagate to DELETED"

        self.__test_fileDelete('/individual-study/yoyo')

      else:
        assert False

    except Exception as e:
      assert False



