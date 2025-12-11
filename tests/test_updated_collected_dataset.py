import unittest
from obiba_mica.update_collected_dataset import CollectedDatasetService
from obiba_mica.legacy import MicaLegacySupport
from tests.utils import Utils

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = CollectedDatasetService(Utils.make_client())
    # Ensure dataset is in expected state before tests
    cls._ensure_dataset_state()

  @classmethod
  def teardown_class(cls):
    # Restore dataset to expected state after tests
    cls._ensure_dataset_state()

  @classmethod
  def _ensure_dataset_state(cls):
    """Ensure cls-wave1 dataset is in the correct state (published, correct project/table)"""
    try:
      # Restore correct project and table values
      cls.service.update('cls-wave1', project='CLS', table='Wave1')
      # Ensure it's published
      try:
        cls.service.publish('cls-wave1')
      except Exception:
        pass  # May already be published
    except Exception:
      pass  # Dataset may not exist, which is fine for some test environments

  def test_1_updateProject(self):
    try:
      response = self.service.update('cls-wave1', project='dummy')
      if response.code == 204:
        # Wait for update to propagate before verifying
        def check_update():
          dataset = self.service.get_dataset('cls-wave1')
          collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
          studyTable = collectedDataset['studyTable']
          return studyTable.get('project') == 'dummy'

        assert Utils.wait_for_condition(check_update, timeout=Utils.get_timeout(10)), "Update did not propagate"
      else:
        assert False

    except Exception as e:
      assert False

  def test_2_updateTable(self):
    try:
      response = self.service.update('cls-wave1', table='dummy')
      if response.code == 204:
        # Wait for update to propagate before verifying
        def check_update():
          dataset = self.service.get_dataset('cls-wave1')
          collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
          studyTable = collectedDataset['studyTable']
          return studyTable.get('table') == 'dummy'

        assert Utils.wait_for_condition(check_update, timeout=Utils.get_timeout(10)), "Update did not propagate"
      else:
        assert False

    except Exception as e:
      assert False

  def test_3_updateProjectTable(self):
    try:
      response = self.service.update('cls-wave1', project='CLS', table='Wave1')
      if response.code == 204:
        # Wait for update to propagate before verifying
        def check_update():
          dataset = self.service.get_dataset('cls-wave1')
          collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
          studyTable = collectedDataset['studyTable']
          return studyTable.get('project') == 'CLS' and studyTable.get('table') == 'Wave1'

        assert Utils.wait_for_condition(check_update, timeout=Utils.get_timeout(10)), "Update did not propagate"
      else:
        assert False

    except Exception as e:
      assert False

  def test_4_unpublish(self):
    try:
      response = self.service.unpublish('cls-wave1')
      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_5_publish(self):
    try:
        response = self.service.publish('cls-wave1')
        assert response.code == 204, f"Publish failed: {response.content}"
    except Exception as e:
        assert False, f"Exception during publish: {e}"


