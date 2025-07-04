import unittest
from obiba_mica.update_collected_dataset import CollectedDatasetService
from obiba_mica.legacy import MicaLegacySupport
from tests.utils import Utils

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = CollectedDatasetService(Utils.make_client())

  def test_1_updateProject(self):
    try:
      response = self.service.update('cls-wave1', project='dummy')
      if response.code == 204:
        dataset = self.service.get_dataset('cls-wave1')
        collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
        studyTable = collectedDataset['studyTable']

        if studyTable['project'] == 'dummy':
          assert True
        else:
          assert False
      else:
        assert False

    except Exception as e:
      assert False

  def test_2_updateTable(self):
    try:
      response = self.service.update('cls-wave1', table='dummy')
      if response.code == 204:
        dataset = self.service.get_dataset('cls-wave1')
        collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
        studyTable = collectedDataset['studyTable']

        if studyTable['table'] == 'dummy':
          assert True
        else:
          assert False
      else:
        assert False

    except Exception as e:
      assert False

  def test_3_updateProjectTable(self):
    try:
      response = self.service.update('cls-wave1', project='CLS', table='Wave1')
      if response.code == 204:
        dataset = self.service.get_dataset('cls-wave1')
        collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
        studyTable = collectedDataset['studyTable']

        if studyTable['project'] == 'CLS' and studyTable['table'] == 'Wave1':
          assert True
        else:
          assert False
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


