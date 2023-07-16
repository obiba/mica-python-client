"""
Mica file management.
"""

import argparse
import json
from obiba_mica.core import MicaClient
import urllib.request
import urllib.parse
import urllib.error
import re
import os

class FileAction(argparse.Action):
  """
  Class used when parsing commandline args to stores the file action and destination
  """
  def __call__(self, parser, namespace, values, option_string=None):
    setattr(namespace, '_file_cmd', self.dest)
    setattr(namespace, self.dest, values)


class StoreTrueFileAction(FileAction):
  """
  Class used when parsing commandline args to set the nargs and const values
  """
  def __init__(self, *args, **kwargs):
    kwargs.update(dict(nargs=0, const=True))
    super(StoreTrueFileAction, self).__init__(*args, **kwargs)

  def __call__(self, parser, namespace, values, option_string=None):
    super(StoreTrueFileAction, self).__call__(
        parser, namespace, self.const, option_string=option_string)


class MicaFile:
  """
  File on Mica file system
  """

  def __init__(self, path):
    self.path = path

  def get_dl_ws(self):
    """
    Returns the file download REST endpoint path
    """
    return '/'.join(['/draft/file-dl', urllib.parse.quote(self.path.strip('/'))])

  def get_ws(self):
    """
    Returns the REST file endpoint path
    """
    return '/'.join(['/draft/file', urllib.parse.quote(self.path.strip('/'))])


class FileService(object):
  """
  Mica filesystem management service
  """

  FILES_WS = '/draft/files'
  STATUS_DRAFT = 'DRAFT'
  STATUS_UNDER_REVIEW = 'UNDER_REVIEW'
  STATUS_DELETED = 'DELETED'

  def __init__(self, client: MicaClient, verbose: bool = False):
    self.client = client
    self.verbose = verbose

  def __make_request(self):
    """
    Builds a request object for a file operation
    """
    request = self.client.new_request()
    request.fail_on_error().accept_json()

    if self.verbose:
        request.verbose()

    return request

  def __validate_status(self, file, status):
    """
    Validates the input request, must match the actual file status
    """
    state = self.get(file).as_json()
    if state['revisionStatus'] != status:
        raise Exception('Invalid file revision status. Found: %s, Required: %s' % (
            state['revisionStatus'], status))

  def get(self, file):
    """
    Retrieves a file from Mica filesystem

    :param file - file path
    """
    return self.__make_request().get().resource(MicaFile(file).get_ws()).send()

  def create(self, path, name):
    """
    Creates a folder

    :param folder - Mica filesystem folder path
    :param name - folder name
    """
    self.__validate_status(path, self.STATUS_DRAFT)
    return self.__make_request().post().resource(self.FILES_WS).content_type_json().content(
        json.dumps(dict(id='', fileName='.', path='/'.join([MicaFile(path).path, name])))).send()

  def copy(self, file, dest):
    """
    Copies a file to another destination in Mica filesystem

    :param file - Mica filesystem file
    :param dest - destination folder
    """
    return self.__make_request().put().resource('%s?copy=%s' % (MicaFile(file).get_ws(), urllib.parse.quote_plus(dest, safe=''))).send()

  def move(self, file, dest):
    """
    Moves a file to another destination in Mica filesystem

    :param file - Mica filesystem file
    :param dest - destination folder
    """
    self.__validate_status(file, self.STATUS_DRAFT)
    return self.__make_request().put().resource('%s?move=%s' % (MicaFile(file).get_ws(), urllib.parse.quote_plus(dest, safe=''))).send()

  def name(self, file, name):
    """
    Renames a file

    :param file - Mica filesystem file
    :param name - new name
    """
    self.__validate_status(file, self.STATUS_DRAFT)
    return self.__make_request().put().resource('%s?name=%s' % (MicaFile(file).get_ws(), urllib.parse.quote_plus(name, safe=''))).send()

  def status(self, file, status):
    """
    Changes a file status (DRAFT, UNDER_REVIEW, DELETED)

    :param file - Mica filesystem file
    :param name - new name
    """
    return self.__make_request().put().resource('%s?status=%s' % (MicaFile(file).get_ws(), status.upper())).send()

  def publish(self, file, published):
    """
    Publishes/ubpublishes a file

    :param file - Mica filesystem file
    :param published - If True, file gets published
    """
    if published:
        self.__validate_status(file, self.STATUS_UNDER_REVIEW)

    return self.__make_request().put().resource('%s?publish=%s' % (MicaFile(file).get_ws(), str(published).lower())).send()

  def unpublish(self, *args):
    """
    Unpublishes a file

    :param file - Mica filesystem file
    """
    return self.publish(False)

  def uploadTempFile(self, upload):
    response = self.__make_request().content_upload(upload).post().resource('/files/temp').send()

    location = None
    if 'Location' in response.headers:
        location = response.headers['Location']
    elif 'location' in response.headers:
        location = response.headers['location']

    job_resource = re.sub(r'http.*\/ws', r'', location)
    return self.__make_request().get().resource(job_resource).send().as_json()


  def upload(self, file, upload):
    """
    Uploads a file to a destination Mica's file system

    :param file - Mica filesystem destination path
    :param upload - local file to upload
    """
    temp_file = self.uploadTempFile(upload)
    fileName = temp_file.pop('name', '')
    temp_file.update(
        dict(fileName=os.path.basename(fileName), justUploaded=True, path=MicaFile(file).path))

    return self.__make_request().post().resource(self.FILES_WS).content_type_json().content(
        json.dumps(temp_file)).send()

  def download(self, file, *args):
    return self.__make_request().get().resource(MicaFile(file).get_dl_ws()).send()

  def   delete(self, file, *args):
    self.__validate_status(file, self.STATUS_DELETED)
    return self.__make_request().delete().resource(MicaFile(file).get_ws()).send()

  @staticmethod
  def add_arguments(parser):
    """
    Add file command specific options

    :param parser - commandline args parser
    """
    parser.add_argument('path', help='File path in Mica file system')
    parser.add_argument('--json', '-j', action='store_true',
                        help='Pretty JSON formatting of the response')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--download', '-dl',
                       action=StoreTrueFileAction, help='Download file')
    group.add_argument('--upload', '-up', action=FileAction,
                       help='Upload a local file to a folder in Mica file system, requires the folder to be in DRAFT state')
    group.add_argument('--create', '-c', action=FileAction,
                       help='Create a folder at a specific location, requires the file to be in DRAFT state')
    group.add_argument('--copy', '-cp', action=FileAction,
                       help='Copy a file to the specified destination')
    group.add_argument('--move', '-mv', action=FileAction,
                       help='Move a file to the specified destination, requires the file to be in DRAFT state')
    group.add_argument('--delete', '-d', action=StoreTrueFileAction,
                       help='Delete a file on Mica file system, requires the file to be in DELETED state')
    group.add_argument('--name', '-n', action=FileAction,
                       help='Rename a file, requires the file to be in DRAFT state')
    group.add_argument('--status', '-st',
                       action=FileAction, help='Change file status')
    group.add_argument('--publish', '-pu', action=StoreTrueFileAction,
                       help='Publish a file, requires the file to be in UNDER_REVIEW state')
    group.add_argument('--unpublish', '-un',
                       action=StoreTrueFileAction, help='Unpublish a file')

  @staticmethod
  def do_command(args):
    """
    Execute file command

    :param args - commandline args
    """
    service = FileService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
    response = None

    if hasattr(args, '_file_cmd'):
      command = getattr(service, args._file_cmd)
      fileCommandParams = getattr(args, args._file_cmd)
      response = command(args.path, fileCommandParams)
    else:
      response = service.get()

    res = response.pretty_json() if args.json and not args.download and not args.upload else response.content

    # output to stdout
    if len(res) > 0:
      print(res)
