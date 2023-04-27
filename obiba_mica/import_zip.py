"""
Import data exported from old mica as zip files.
"""

from obiba_mica.core import MicaClient
import os.path
import os

class FileImportService:

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def __make_request(self):
      request = self.client.new_request()
      request.method('POST')
      request.fail_on_error()
      request.content_type('multipart/form-data')
      request.accept_json()
      if self.verbose:
          request.verbose()
      return request

  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options
      """
      parser.add_argument('path', help='Path to the zip file or directory that contains zip files to be imported')
      parser.add_argument('--publish', '-pub', action='store_true', help='Publish imported study')

  def import_zip(self, path, publish: bool = None):
      """
      Import the Zip file content
      """
      print("Importing " + path + "...")

      query = "publish=%s" % str(publish).lower() if publish is not None and publish else ''
      return self.__make_request().content_upload(path).resource('/draft/studies/_import?%s' % query).send()

  @classmethod
  def __printResponse(cls, response):
    res = response.content
    # output to stdout
    if len(res) > 0:
        print(res)

  @classmethod
  def do_command(cls, args):
      service = FileImportService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)

      """
      Execute Import Zip command
      """
      if args.path.endswith('.zip'):
          cls.__printResponse(service.import_zip(args.path, args.publish))
      else:
          for export_file in os.listdir(args.path):
              if export_file.endswith('.zip'):
                  cls.__printResponse(service.import_zip(args.path + '/' + export_file))
