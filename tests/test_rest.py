import unittest
from obiba_mica.rest import RestService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.service = RestService(Utils.make_client())

  def test_validRestCall(self):
    try:
      response = self.service.send_get_request('/draft/individual-study/clsa').as_json()
      if response['id'] != 'clsa':
        assert False

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
