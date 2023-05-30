"""
Mica annotations management.
"""

import sys
from obiba_mica.core import MicaClient, UriBuilder
import csv

class AnnotationService:
  """
  Service exports annotations of variables of one or all collected datasets of a Mica server
  """

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def __make_request(self):
    request = self.client.new_request()
    if self.verbose:
        request.verbose()
    return request

  def __send_request(self, ws):
    """
    Create a new request
    """
    attemps = 0
    success = False
    response = None
    while (attemps<10 and not success):
      try:
        attemps += 1
        request = self.__make_request()
        response = request.get().resource(ws).send()
        success = True
      except Exception as e:
        print(e, file=sys.stderr)

    if self.verbose:
        print(response.pretty_json())

    return response.as_json()

  def create_writer(self, outputFile: str = None):
    """
    Creates a CSV writer associated with an output file if provided, otherwise the output is sent to STDOUT

    :param outputFile - csv output file
    """
    file = sys.stdout
    if outputFile:
        file = open(outputFile, 'w')
    writer = csv.DictWriter(file, fieldnames=['study','dataset','name','index','label', 'annotation'],
        escapechar='"', quotechar='"', quoting=csv.QUOTE_ALL)

    return writer

  def write_dataset_variable_annotations(self, datasetId, writer):
    """
    Writes annotations of all vatiables of one collected dataset

    :param datasetId - collected dataset ID
    :param writer - csv writer
    """

    # send request to get total count
    ws = UriBuilder(['collected-dataset', datasetId, 'variables']).query('from', 0).query('limit', 0).build()
    response = self.__send_request(ws)
    total = response['total'] if 'total' in response else 0

    f = 0
    while total > 0 and f < total:
      ws = UriBuilder(['collected-dataset', datasetId, 'variables']).query('from', f).query('limit', 1000).build()
      response = self.__send_request(ws)
      f = f + 1000
      # format response
      if 'variables' in response:
        for var in response['variables']:
          label = ''
          if 'attributes' in var:
            for attr in var['attributes']:
              if attr['name'] == 'label':
                  label = attr['values'][0]['value']
            for attr in var['attributes']:
              if 'namespace' in attr:
                tag = attr['namespace'] + '::' + attr['name'] + '.' + attr['values'][0]['value']
                writer.writerow({'study': var['studyId'],
                  'dataset': var['datasetId'],
                  'name': var['name'],
                  'index': str(var['index']),
                  'label': label,
                  'annotation': tag
                  })

  def write_datasets_variable_annotations(self, writer):
    """
    In case no dataset is provided, write the annotations of all variables of all collected datasets

    :param writer - csv writer
    """
    ws = UriBuilder(['collected-datasets']).query('from', 0).query('limit', 0).build()
    response = self.__send_request(ws)
    total = response['total'] if 'total' in response else 0

    f = 0
    while total > 0 and f < total:
      ws = UriBuilder(['collected-datasets']).query('from', f).query('limit', 100).build()
      response = self.__send_request(ws)
      f = f + 100
      if 'datasets' in response:
        i = 0
        for ds in response['datasets']:
          try:
            self.write_dataset_variable_annotations(ds['id'], writer)
            i += 1
          except Exception as e:
            print('Failed to write annotations of dataset %s' % ds['id'])
          if i > 4:
            break

  @classmethod
  def add_arguments(cls, parser):
      """
      Add annotations command specific options

      :param parser - commandline args parser
      """
      parser.add_argument('--out', '-o', required=False, help='Output file (default is stdout)')
      parser.add_argument('--dataset', '-d', required=False, help='Study dataset ID')

  @classmethod
  def do_command(cls, args):
    """
    Execute annotations command

    :param args - commandline args
    """
    service  = AnnotationService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
    writer = service.create_writer(args.out)
    writer.writeheader()

    if args.dataset == None:
        service.write_datasets_variable_annotations(writer)
    else:
      service.write_dataset_variable_annotations(args.dataset, writer)
