"""
Import data exported from old mica as zip files.
"""

from obiba_mica.core import MicaClient
import os.path
import os

class FileImportService:
  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options
      """
      parser.add_argument('path', help='Path to the zip file or directory that contains zip files to be imported')
      parser.add_argument('--publish', '-pub', action='store_true', help='Publish imported study')

  @classmethod
  def import_zip(cls, args, path):
      """
      Import the Zip file content
      """
      print("Importing " + path + "...")
      # Build and send request
      request = MicaClient.build(MicaClient.LoginInfo.parse(args)).new_request()
      request.fail_on_error()

      if args.verbose:
          request.verbose()

      # send request
      request.content_upload(path).accept_json().content_type('multipart/form-data')
      response = request.post().resource('/draft/studies/_import?publish=' + str(args.publish).lower()).send()

      # format response
      res = response.content

      # output to stdout
      if len(res) > 0:
          print(res)

  @classmethod
  def do_command(cls, args):
      """
      Execute Import Zip command
      """
      if args.path.endswith('.zip'):
          cls.import_zip(args, args.path)
      else:
          for export_file in os.listdir(args.path):
              if export_file.endswith('.zip'):
                  cls.import_zip(args, args.path + '/' + export_file)


