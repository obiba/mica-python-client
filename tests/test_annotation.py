import unittest
from obiba_mica.annotation import AnnotationService
from obiba_mica.core import MicaClient
from tests.utils import Utils
from os import path, remove

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = AnnotationService(Utils.make_client())

  def test_datasetAnnotation(self):
    try:
      outputFile = '/tmp/cls-wave1.csv'
      writer = self.service.create_writer(outputFile)
      writer.writeheader()

      self.service.write_dataset_variable_annotations('cls-wave1', writer)

      if path.exists(outputFile):
        remove(outputFile)
      else:
        assert False

      assert True
    except Exception as e:
      assert False
