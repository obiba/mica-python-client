import unittest
import time
from obiba_mica.update_collected_datasets import CollectedDatasetsService
from obiba_mica.legacy import MicaLegacySupport
from obiba_mica.core import HTTPError
from tests.utils import Utils

class TestClass(unittest.TestCase):
  datasets = None

  @classmethod
  def setup_class(cls):
    cls.service = CollectedDatasetsService(Utils.make_client())


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
    tries = 3
    for attempt in range(tries):
      try:
        response = self.service.unpublish(dataset['id'])
        if response.code == 204:
          return
        else:
          assert False, f"Unexpected response code while unpublishing {dataset['id']}: {response.code}"
      except HTTPError as e:
        # Retry on server errors (5xx)
        if e.is_server_error() and attempt < tries - 1:
          time.sleep(2 ** attempt)
          continue
        assert False, f"HTTPError while unpublishing {dataset['id']}: {e}"
      except Exception as e:
        assert False, f"Exception while unpublishing {dataset['id']}: {e}"

  def __publish(self, dataset):
    tries = 3
    for attempt in range(tries):
      try:
        response = self.service.publish(dataset['id'])
        if response.code == 204:
          return
        else:
          assert False, f"Unexpected response code while publishing {dataset['id']}: {response.code}"
      except HTTPError as e:
        # Retry on server errors (5xx)
        if e.is_server_error() and attempt < tries - 1:
          time.sleep(2 ** attempt)
          continue
        assert False, f"HTTPError while publishing {dataset['id']}: {e}"
      except Exception as e:
        assert False, f"Exception while publishing {dataset['id']}: {e}"


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
