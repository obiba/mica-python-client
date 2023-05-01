import unittest
from obiba_mica.perm import IndividualStudyPermissionService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = IndividualStudyPermissionService(Utils.make_client())

  def test_documentPermission(self):
    try:
      response = self.service.add_permission('clsa', 'USER', 'user1', 'READER')
      assert response.code == 204

      response = self.service.list_permissions('clsa').as_json()
      found = next((x for x in response if x['principal'] == 'user1'), None)

      if found is None:
        assert False

      response = self.service.delete_permission('clsa', 'USER', 'user1')
      assert response.code == 204

    except Exception as e:
      assert False
