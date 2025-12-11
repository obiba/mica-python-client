import unittest
from obiba_mica.access import IndividualStudyAccessService, FileAccessService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def test_documentAccess(self):
    self.service = IndividualStudyAccessService(Utils.make_client())

    try:
      response = self.service.add_access('clsa', 'USER', 'user1')
      assert response.code == 204

      # Wait for access to be indexed/available
      def check_access():
        response = self.service.list_accesses('clsa').as_json()
        found = next((x for x in response if x['principal'] == 'user1'), None)
        return found is not None

      assert Utils.wait_for_condition(check_access, timeout=Utils.get_timeout(10)), "Access not found after add"

      response = self.service.delete_access('clsa', 'USER', 'user1')
      assert response.code == 204
    except Exception as e:
      assert False

  def test_fileAccess(self):
    self.service = FileAccessService(Utils.make_client())

    try:
      file = '/individual-study/cls/population/1/data-collection-event/4/Wave 4 subject interview.pdf'
      response = self.service.add_access(file, 'USER', 'user1')
      assert response.code == 204

      # Wait for access to be indexed/available
      def check_access():
        response = self.service.list_accesses(file).as_json()
        found = next((x for x in response if x['principal'] == 'user1'), None)
        return found is not None

      assert Utils.wait_for_condition(check_access, timeout=Utils.get_timeout(10)), "File access not found after add"

      response = self.service.delete_access(file, 'USER', 'user1')
      assert response.code == 204
    except Exception as e:
      assert False

