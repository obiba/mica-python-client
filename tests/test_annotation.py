import unittest
from obiba_mica.annotation import AnnotationService
from tests.utils import Utils
from os import path, remove

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    AnnotationService.add_arguments(self.parser)

  def test_datasetAnnotation(self):
    try:
      outputFile = '/tmp/cls-wave1.csv'
      args = Utils.parse_arg_values(parser=self.parser,params=['--dataset', 'cls-wave1', '--out', outputFile])
      AnnotationService.do_command(args)

      if path.exists(outputFile):
        remove(outputFile)
      else:
        assert False

      assert True
    except Exception as e:
      assert False
      
