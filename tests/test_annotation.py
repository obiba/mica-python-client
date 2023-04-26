import unittest
from obiba_mica.annotation import AnnotationService
from obiba_mica.core import MicaClient
from tests.utils import Utils
from os import path, remove

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    AnnotationService.add_arguments(self.parser)

  def test_datasetAnnotation(self):
    try:
      outputFile = '/tmp/cls-wave1.csv'
      service  = AnnotationService(Utils.make_client())
      writer = service.create_writer(outputFile)
      writer.writeheader()

      service.write_dataset_variable_annotations('cls-wave1', writer)

      if path.exists(outputFile):
        remove(outputFile)
      else:
        assert False

      assert True
    except Exception as e:
      assert False
      
