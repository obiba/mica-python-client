import unittest
from obiba_mica.file import FileService
from tests.utils import Utils
import json

class TestClass(unittest.TestCase):

  def setup_class(self):
    self.parser = Utils.make_arg_parser()
    FileService.add_arguments(self.parser)

  def test_1_fileUpload(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--upload', './tests/resources/dummy.csv', '/individual-study/clsa'])
      FileService.do_command_internal(args)
      assert True
    except Exception as e:
      assert False    

  def test_2_fileChangeStatus(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--status', 'UNDER_REVIEW', '/individual-study/clsa/dummy.csv'])
      FileService.do_command_internal(args)
      assert True
    except Exception as e:
      assert False    

  def test_3_filePublish(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--publish', '/individual-study/clsa/dummy.csv'])
      FileService.do_command_internal(args)
      assert True
    except Exception as e:
      assert False    

  def test_4_fileJson(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['/individual-study/clsa/dummy.csv'])
      res = FileService.do_command_internal(args)

      if res is None:
        assert False
      else:
        parsed = json.loads(res)
        if parsed['name'] != 'dummy.csv' and parsed['state']['publishedId'] == None:
          assert False

      assert True
    except Exception as e:
      assert False    

  def test_5_fileDownload(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--download', './individual-study/clsa/dummy.csv'])
      content = FileService.do_command_internal(args)

      if 'col1' not in content:
        assert False

      assert True
    except Exception as e:
      assert False    


  def test_6_fileDelete(self):
    try:
      args = Utils.parse_arg_values(parser=self.parser,params=['--status', 'DELETED', '/individual-study/clsa/dummy.csv'])
      FileService.do_command_internal(args)

      args = Utils.parse_arg_values(parser=self.parser,params=['--delete', '/individual-study/clsa/dummy.csv'])
      FileService.do_command_internal(args)

      assert True
    except Exception as e:
      assert False