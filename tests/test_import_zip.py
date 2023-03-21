import unittest
from obiba_mica.import_zip import FileImportService
from obiba_mica.rest import RestService
from tests.utils import Utils

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    FileImportService.add_arguments(self.parser)

  def test_importZip(self):
    args = Utils.parse_arg_values(parser=self.parser,params=['./tests/resources/dummy-test-study.zip'])
    FileImportService.do_command(args)


