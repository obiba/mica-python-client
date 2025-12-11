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

      # Wait for permission to be indexed/available
      def check_permission():
        response = self.service.list_permissions('clsa').as_json()
        found = next((x for x in response if x['principal'] == 'user1'), None)
        return found is not None

      assert Utils.wait_for_condition(check_permission, timeout=Utils.get_timeout(10)), "Permission not found after add"

      response = self.service.delete_permission('clsa', 'USER', 'user1')
      assert response.code == 204

    except Exception as e:
      assert False
