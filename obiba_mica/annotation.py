"""
Mica tags management.
"""

import sys
import pycurl
from obiba_mica.core import MicaClient, UriBuilder
import csv

class AnnotationService:
  @classmethod
  def add_arguments(cls, parser):
      """
      Add tags command specific options
      """
      parser.add_argument('--out', '-o', required=False, help='Output file (default is stdout)')
      parser.add_argument('--dataset', '-d', required=False, help='Study dataset ID')

  @classmethod
  def send_request(cls, client, ws, verbose=False):
      """
      Create a new request
      """
      attemps = 0
      success = False
      response = None
      while (attemps<10 and not success):
          try:
              attemps += 1
              request = client.new_request()
              if verbose:
                  request.verbose()
              response = request.get().resource(ws).send()
              success = True
          except Exception as e:
              print(e, file=sys.stderr)
          except pycurl.error as error:
              errno, errstr = error
              print('An error occurred: ', errstr, file=sys.stderr)

      if verbose:
          print(response.pretty_json())
      return response.as_json()

  @classmethod
  def write_dataset_variable_tags(cls, client, dataset, writer, verbose=False):
      # send request to get total count
      ws = UriBuilder(['collected-dataset', dataset, 'variables']).query('from', 0).query('limit', 0).build()
      response = cls.send_request(client, ws, verbose)
      total = response['total'] if 'total' in response else 0

      f = 0
      while total > 0 and f < total:
          ws = UriBuilder(['collected-dataset', dataset, 'variables']).query('from', f).query('limit', 1000).build()
          response = cls.send_request(client, ws, verbose)
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
                                  'tag': tag
                                  })

  @classmethod
  def do_command(cls, args):
      """
      Execute tags command
      """
      file = sys.stdout
      if args.out:
          file = open(args.out, 'w')
      writer = csv.DictWriter(file, fieldnames=['study','dataset','name','index','label', 'tag'],
          escapechar='"', quotechar='"', quoting=csv.QUOTE_ALL)
      writer.writeheader()
      client = MicaClient.build(MicaClient.LoginInfo.parse(args))

      if args.dataset == None:
          ws = UriBuilder(['collected-datasets']).query('from', 0).query('limit', 0).build()
          response = cls.send_request(client, ws, args.verbose)
          total = response['total'] if 'total' in response else 0

          f = 0
          while total > 0 and f < total:
              ws = UriBuilder(['collected-datasets']).query('from', f).query('limit', 100).build()
              response = cls.send_request(client, ws, args.verbose)
              f = f + 100
              if 'datasets' in response:
                  for ds in response['datasets']:
                       cls.write_dataset_variable_tags(client, ds['id'], writer, args.verbose)
      else:
           cls.write_dataset_variable_tags(client, args.dataset, writer, args.verbose)
