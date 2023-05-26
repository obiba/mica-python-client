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
