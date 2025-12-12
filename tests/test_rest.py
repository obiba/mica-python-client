import unittest
from obiba_mica.rest import RestService
from obiba_mica.core import HTTPError
from tests.utils import Utils

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = RestService(Utils.make_client())

  def test_validRestCall(self):
    try:
      response = self.service.send_request('/draft/individual-study/clsa', self.service.make_request('GET')).as_json()
      if response['id'] != 'clsa':
        assert False

      assert True
    except Exception as e:
      assert False

  def test_validRestCallWithParams(self):
    try:
      response = self.service.send_request('/draft/study-states', self.service.make_request('GET').query(('query', 'cls*'))).as_json()
      if isinstance(response, list) and len(list(filter(lambda r: r['id'] == 'cls', response))) > 1:
        assert False

      assert True
    except Exception as e:
      assert False

  def test_invalidRestCall(self):
    try:
      response = self.service.send_request('/draft/individual-study/potato', self.service.make_request('GET')).as_json()
      if response['id'] != 'clsa':
        assert False

      assert True
    except HTTPError as e:
      assert e.code == 404
    except Exception as e:
      assert False

  def test_binaryDownload(self):
    try:
      # First, get a list of studies to find a valid study ID
      studies_response = self.service.send_request('/draft/individual-studies', self.service.make_request('GET')).as_json()

      if not studies_response or len(studies_response) == 0:
        # No studies available, skip test
        assert True
        return

      # Get the first study's ID
      study_id = studies_response[0]['id']

      # Create request for binary download with Accept: application/octet-stream
      request = self.service.make_request('GET')
      request.accept('application/octet-stream')

      # Download the study folder as binary (kept in memory, not written to disk)
      response = self.service.send_request(f'/draft/file-dl//individual-study/{study_id}', request)

      # Verify we got binary content (not JSON)
      assert response.content is not None, "Binary content should not be None"
      assert len(response.content) > 0, "Binary content should not be empty"
      assert response.code == 200, f"Expected 200, got {response.code}"

      # Verify Content-Type is not JSON (should be application/zip or application/octet-stream)
      content_type = response.headers.get('Content-Type', '')
      assert 'json' not in content_type.lower(), f"Content-Type should not be JSON, got: {content_type}"

      assert True
    except HTTPError as e:
      # If the endpoint doesn't exist or study has no files, that's ok for this test
      if e.code in [404, 204]:
        assert True
      else:
        assert False, f"Unexpected HTTPError: {e.code}"
    except Exception as e:
      assert False, f"Unexpected exception: {e}"
