import unittest
from obiba_mica.update_collected_datasets import CollectedDatasetsService
from obiba_mica.legacy import MicaLegacySupport
from obiba_mica.core import HTTPError
from tests.utils import Utils

class TestClass(unittest.TestCase):
  datasets = None

  @classmethod
  def setup_class(cls):
    cls.service = CollectedDatasetsService(Utils.make_client())
    # Ensure datasets are in expected state before tests
    cls._ensure_datasets_state()

  @classmethod
  def teardown_class(cls):
    # Restore datasets to expected state after tests
    cls._ensure_datasets_state()

  @classmethod
  def _ensure_datasets_state(cls):
    """Ensure cls datasets are in the correct state (published, correct project)"""
    try:
      datasets = cls.service.get_datasets('^cls-')
      for dataset in datasets:
        try:
          # Restore correct project value
          cls.service.update(dataset['id'], 'CLS')
          # Ensure it's published
          try:
            cls.service.publish(dataset['id'])
          except Exception:
            pass  # May already be published
        except Exception:
          pass  # Individual dataset cleanup failure
    except Exception:
      pass  # Datasets may not exist, which is fine for some test environments


  def __updateProjects(self, dataset, project: str):
    try:
      datasetId = dataset['id']
      response = self.service.update(datasetId, project)
      if response.code == 204:
        dataset = self.service.get_dataset(datasetId)
        collectedDataset = MicaLegacySupport.getCollectedDataset(dataset)
        studyTable = collectedDataset['studyTable']

        if studyTable['project'] == project:
          assert True
        else:
          assert False
      else:
        assert False

    except Exception as e:
      assert False

  def __unpublish(self, dataset):
    def try_unpublish():
      try:
        response = self.service.unpublish(dataset['id'])
        if response.code == 204:
          return True
        else:
          # Unexpected response code, fail immediately
          assert False, f"Unexpected response code while unpublishing {dataset['id']}: {response.code}"
      except HTTPError as e:
        # Retry on server errors (5xx), fail immediately on client errors (4xx)
        if e.is_server_error():
          return False
        assert False, f"HTTPError while unpublishing {dataset['id']}: {e}"

    # Retry with exponential backoff: 1s, 2s, 4s - longer timeout in CI
    timeout = Utils.get_timeout(7)  # 7s local, 21s in CI
    success = Utils.wait_for_condition(try_unpublish, timeout=timeout, interval=1, backoff='exponential')
    assert success, f"Failed to unpublish {dataset['id']} after retries"

  def __publish(self, dataset):
    def try_publish():
      try:
        response = self.service.publish(dataset['id'])
        if response.code == 204:
          return True
        else:
          # Unexpected response code, fail immediately
          assert False, f"Unexpected response code while publishing {dataset['id']}: {response.code}"
      except HTTPError as e:
        # Retry on server errors (5xx), fail immediately on client errors (4xx)
        if e.is_server_error():
          return False
        assert False, f"HTTPError while publishing {dataset['id']}: {e}"

    # Retry with exponential backoff: 1s, 2s, 4s - longer timeout in CI
    timeout = Utils.get_timeout(7)  # 7s local, 21s in CI
    success = Utils.wait_for_condition(try_publish, timeout=timeout, interval=1, backoff='exponential')
    assert success, f"Failed to publish {dataset['id']} after retries"


  def test_1_getDatasets(self):
    try:
      datasets = self.service.get_datasets('^cls-')
      if len(datasets) > 0:
        TestClass.datasets = datasets
      else:
        assert False

    except Exception as e:
      assert False

  def test_2_updateDummyProject(self):
    try:
      for dataset in TestClass.datasets:
        self.__updateProjects(dataset, 'dummy')

    except Exception as e:
      assert False

  def test_3_updateCorrectProject(self):
    for dataset in TestClass.datasets:
      self.__updateProjects(dataset, 'CLS')

  def test_4_unpublish(self):
    for dataset in TestClass.datasets:
      self.__unpublish(dataset)

  def test_5_publish(self):
    for dataset in TestClass.datasets:
      self.__publish(dataset)
