import unittest
from obiba_mica.update_collected_datasets import CollectedDatasetsService
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
        studyTable = dataset['obiba.mica.CollectedDatasetDto.type']['studyTable']

        if studyTable['project'] == project:
          assert True
        else:
          assert False
      else:
        assert False

    except Exception as e:
      assert False

  def __unpublish(self, dataset):
    try:
      response = self.service.unpublish(dataset['id'])
      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def __publish(self, dataset):
    try:
      response = self.service.publish(dataset['id'])
      if response.code == 204:
        assert True
      else:
        assert False

    except Exception as e:
      assert False


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
