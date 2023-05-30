'''
Mica search query.
'''

import json
import sys
from obiba_mica.core import MicaClient, UriBuilder
import csv
from io import StringIO

class SearchService:

  def __init__(self, client: MicaClient, verbose: bool = False):
    self.client = client
    self.verbose = verbose

  def __make_request(self):
    request = self.client.new_request()
    request.fail_on_error()
    request.post()
    request.accept_json()
    if self.verbose:
        request.verbose()
    return request

  def send_search_request(self, ws, query):
      '''
      Create a new search request

      :param ws - REST endpoint (/variables/_rql)
      :param query - RQL query
      '''
      try:
          request = self.__make_request()
          response = request.resource(ws).content_type_form().form({'query': query}).send()
          return response.as_json()
      except Exception as e:
          print(e, file=sys.stderr)

      return None

  def __as_rql(self, name, args):
      return name + '(' + ','.join(args) + ')'

  def __append_rql(self, query, target, select, sort, start, limit, locale):
      _fields = self.__as_rql('fields(', select) + ')'
      _sort = self.__as_rql('sort', sort)
      _limit = self.__as_rql('limit', [str(start), str(limit)])
      statement = ','.join([_fields, _limit, _sort])
      # normalize
      q = query
      if q == None or q == '':
          q = target + '()'

      # hack: replace target call with statement
      if target + '()' in q:
          q = q.replace(target + '()', target + '(' + statement + ')')
      elif target + '(' in q:
          q = q.replace(target + '(', target + '(' + statement + ',')
      else:
          q = target + '(' + statement + '),' + q

      return q + ',locale(' + locale + ')'

  def __extract_label(self, labels, locale='en', locale_key='lang', value_key='value'):
      if not labels:
          return None
      label_und = None
      if labels:
          for label in labels:
              if label[locale_key] == locale:
                  return label[value_key]
              if label[locale_key] == 'und':
                  label_und = label[value_key]
      return label_und if label_und else ''

  def __new_writer(self, out, headers):
      file = sys.stdout
      if out:
          if isinstance(out, StringIO):
            file = out
          else:
            file = open(out, 'w')
      writer = csv.DictWriter(file, fieldnames=headers, escapechar='"', quotechar='"', quoting=csv.QUOTE_ALL)
      writer.writeheader()
      return writer

  def __to_string(self, value):
      if value == None:
          return ''
      return str(value)

  def __flatten(self, content, locale='en'):
      flat = {}
      for key in list(content.keys()):
          value = content[key]
          if type(value) is dict:
              fvalue = self.__flatten(value, locale)
              for k in fvalue:
                  nk = key + '.' + k if k != locale else key
                  flat[nk] = fvalue[k]
          elif type(value) is list:
              flat[key] = '|'.join(map(self.__to_string, value))
          else:
              flat[key] = self.__to_string(value)
      return flat

  def search_networks(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published networks matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """

      q = self.__append_rql(query, 'network', ['*'], ['id'], start, limit, locale)
      ws = UriBuilder(['networks', '_rql']).build()
      res = self.send_search_request(ws, q)
      if 'networkResultDto' in res and 'obiba.mica.NetworkResultDto.result' in res['networkResultDto'] and res['networkResultDto']['totalHits'] > 0:
          headers = ['id', 'name', 'acronym', 'description', 'studyIds']
          for item in res['networkResultDto']['obiba.mica.NetworkResultDto.result']['networks']:
              if 'content' in item:
                  item['flat'] = self.__flatten(json.loads(item['content']), locale)
                  for key in list(item['flat'].keys()):
                      if key not in headers:
                          headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['networkResultDto']['obiba.mica.NetworkResultDto.result']['networks']:
              row = {
                  'id': item['id'],
                  'name': self.__extract_label(item['name'], locale),
                  'description': self.__extract_label(item['description'], locale) if 'description' in item else '',
                  'acronym': self.__extract_label(item['acronym'], locale),
                  'studyIds': '|'.join(item['studyIds']) if 'studyIds' in item else ''
              }
              if 'flat' in item:
                  for key in item['flat']:
                      row[key] = item['flat'][key]
              writer.writerow(row)

  def __search_studies(self, query='', start=0, limit=100, locale='en', out=None):
      q = self.__append_rql(query, 'study', ['acronym', 'name', 'objectives', 'model'], ['id'], start, limit, locale)
      ws = UriBuilder(['studies', '_rql']).build()
      res = self.send_search_request(ws, q)
      if 'studyResultDto' in res and 'obiba.mica.StudyResultDto.result' in res['studyResultDto'] and res['studyResultDto']['totalHits'] > 0:
          headers = ['id', 'name', 'acronym', 'objectives']
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              if 'content' in item:
                  item['flat'] = self.__flatten(json.loads(item['content']), locale)
                  for key in list(item['flat'].keys()):
                      if key not in headers:
                          headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              row = {
                  'id': item['id'],
                  'name': self.__extract_label(item['name'], locale),
                  'objectives': self.__extract_label(item['objectives'], locale) if 'objectives' in item else '',
                  'acronym': self.__extract_label(item['acronym'], locale)
              }
              if 'flat' in item:
                  for key in item['flat']:
                      row[key] = item['flat'][key]
              writer.writerow(row)

  def search_studies(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published individual studies matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      typeQuery = self.__as_rql('study', [self.__as_rql('in', ['Mica_dataset.className', 'Study'])])
      theQuery = '%s,%s' % (typeQuery, query) if query is not None and len(query) > 0 else typeQuery
      self.__search_studies(theQuery, start, limit, locale, out)

  def search_initiatives(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published initiatives matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      typeQuery = self.__as_rql('study', [self.__as_rql('in', ['Mica_dataset.className', 'HarmonizationStudy'])])
      theQuery = '%s,%s' % (typeQuery, query) if query is not None and len(query) > 0 else typeQuery
      self.__search_studies(theQuery, start, limit, locale, out)


  def search_study_populations(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches the populations of a individual studies matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      q = self.__append_rql(query, 'study', ['populations.name', 'populations.description', 'populations.model'], ['id'], start, limit, locale)
      ws = UriBuilder(['studies', '_rql']).build()
      res = self.send_search_request(ws, q)
      if 'studyResultDto' in res and 'obiba.mica.StudyResultDto.result' in res['studyResultDto']:
          headers = ['id', 'name', 'description', 'studyId']
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              if 'populationSummaries' in item:
                  for pop in item['populationSummaries']:
                      if 'content' in pop:
                          pop['flat'] = self.__flatten(json.loads(pop['content']), locale)
                          for key in list(pop['flat'].keys()):
                              if key not in headers:
                                  headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              if 'populationSummaries' in item:
                  for pop in item['populationSummaries']:
                      row = {
                          'id': item['id'] + ':' + pop['id'],
                          'name': self.__extract_label(pop['name'], locale),
                          'description': self.__extract_label(pop['description'], locale) if 'description' in pop else '',
                          'studyId': item['id']
                      }
                      if 'flat' in pop:
                          for key in pop['flat']:
                              row[key] = pop['flat'][key]
                      writer.writerow(row)

  def search_study_dces(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published data collection events of individual studies matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      q = self.__append_rql(query, 'study', ['populations.dataCollectionEvents'], ['id'], start, limit, locale)
      ws = UriBuilder(['studies', '_rql']).build()
      res = self.send_search_request(ws, q)
      if 'studyResultDto' in res and 'obiba.mica.StudyResultDto.result' in res['studyResultDto']:
          headers = ['id', 'name', 'description', 'studyId', 'populationId', 'start', 'end']
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              if 'populationSummaries' in item:
                  for pop in item['populationSummaries']:
                      if 'dataCollectionEventSummaries' in pop:
                          for dce in pop['dataCollectionEventSummaries']:
                              if 'content' in dce:
                                  dce['flat'] = self.__flatten(json.loads(dce['content']), locale)
                                  for key in list(dce['flat'].keys()):
                                      if key not in headers:
                                          headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['studyResultDto']['obiba.mica.StudyResultDto.result']['summaries']:
              if 'populationSummaries' in item:
                  for pop in item['populationSummaries']:
                      if 'dataCollectionEventSummaries' in pop:
                          for dce in pop['dataCollectionEventSummaries']:
                              row = {
                                  'id': item['id'] + ':' + pop['id'] + ':' + dce['id'],
                                  'name': self.__extract_label(dce['name'], locale),
                                  'description': self.__extract_label(dce['description'], locale) if 'description' in dce else '',
                                  'studyId': item['id'],
                                  'populationId': item['id'] + ':' + pop['id'],
                                  'start': dce['start'] if 'start' in dce else '',
                                  'end': dce['end'] if 'end' in dce else ''
                              }
                              if 'flat' in dce:
                                  for key in dce['flat']:
                                      row[key] = dce['flat'][key]
                              writer.writerow(row)

  def __search_datasets(self, query='', start=0, limit=100, locale='en', out=None):
      q = self.__append_rql(query, 'dataset', ['*'], ['id'], start, limit, locale)
      ws = UriBuilder(['datasets', '_rql']).build()
      res = self.send_search_request(ws, q)
      if 'datasetResultDto' in res and 'obiba.mica.DatasetResultDto.result' in res['datasetResultDto']:
          headers = ['id', 'name', 'acronym', 'description', 'variableType', 'entityType', 'studyId', 'populationId', 'dceId']
          for item in res['datasetResultDto']['obiba.mica.DatasetResultDto.result']['datasets']:
              if 'content' in item:
                  item['flat'] = self.__flatten(json.loads(item['content']), locale)
                  for key in list(item['flat'].keys()):
                      if key not in headers:
                          headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['datasetResultDto']['obiba.mica.DatasetResultDto.result']['datasets']:
              study_id = ''
              population_id = ''
              dce_id = ''
              if 'obiba.mica.CollectedDatasetDto.type' in item:
                  study_id = item['obiba.mica.CollectedDatasetDto.type']['studyTable']['studyId']
                  population_id = study_id + ':' + item['obiba.mica.CollectedDatasetDto.type']['studyTable']['populationId']
                  dce_id = item['obiba.mica.CollectedDatasetDto.type']['studyTable']['dceId']
              if 'obiba.mica.HarmonizedDatasetDto.type' in item:
                  study_id = item['obiba.mica.HarmonizedDatasetDto.type']['harmonizationTable']['studyId']
              row = {
                  'id': item['id'],
                  'name': self.__extract_label(item['name'], locale),
                  'acronym': self.__extract_label(item['acronym'], locale),
                  'description': self.__extract_label(item['description'], locale) if 'description' in item else '',
                  'variableType': item['variableType'],
                  'entityType': item['entityType'],
                  'studyId': study_id,
                  'populationId': population_id,
                  'dceId': dce_id
              }
              if 'flat' in item:
                  for key in item['flat']:
                      row[key] = item['flat'][key]
              writer.writerow(row)

  def search_datasets(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published collected datasets matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      typeQuery = self.__as_rql('dataset', [self.__as_rql('in', ['Mica_dataset.className', 'StudyDataset'])])
      theQuery = '%s,%s' % (typeQuery, query) if query is not None and len(query) > 0 else typeQuery
      self.__search_datasets(theQuery, start, limit, locale, out)

  def search_protocols(self, query='', start=0, limit=100, locale='en', out=None):
      """
      Searches all published harmonization protocols matching the given query

      :param query - RQL query
      :param start - starting index from which to retrieve data
      :param limit - length of data to be retrieved
      :param locale - default is 'en'
      :param out - output file, if ignored the result is send to STDOUT
      """
      typeQuery = self.__as_rql('dataset', [self.__as_rql('in', ['Mica_dataset.className', 'HarmonizationDataset'])])
      theQuery = '%s,%s' % (typeQuery, query) if query is not None and len(query) > 0 else typeQuery
      self.__search_datasets(theQuery, start, limit, locale, out)

  def search_variables(self, query='', start=0, limit=100, locale='en', out=None):
      q = self.__append_rql(query, 'variable', ['*'], ['id'], start, limit, locale)
      ws = UriBuilder(['variables', '_rql']).build()
      res = self.send_search_request(ws, q)

      def category_label(category):
          if 'attributes' in category:
              labels = [self.__extract_label(label['values'], locale) for label in [a for a in category['attributes'] if a['name'] == 'label']]
              return labels[0] if len(labels) > 0 else ''
          else:
              return ''

      if 'variableResultDto' in res and 'obiba.mica.DatasetVariableResultDto.result' in res['variableResultDto']:
          headers = ['id', 'name', 'label', 'description', 'valueType', 'nature', 'categories', 'categories.missing', 'categories.label',
                    'datasetId', 'studyId', 'populationId', 'dceId',
                    'variableType', 'mimeType', 'unit', 'referencedEntityType', 'repeatable', 'occurrenceGroup']
          for item in res['variableResultDto']['obiba.mica.DatasetVariableResultDto.result']['summaries']:
              if 'annotations' in item:
                  for annot in item['annotations']:
                      key = annot['taxonomy'] + '.' + annot['vocabulary']
                      if key not in headers:
                          headers.append(key)
          writer = self.__new_writer(out, headers)
          for item in res['variableResultDto']['obiba.mica.DatasetVariableResultDto.result']['summaries']:
              row = {
                  'id': item['id'],
                  'name': item['name'],
                  'label': self.__extract_label(item['variableLabel'], locale) if 'variableLabel' in item else '',
                  'description': self.__extract_label(item['description'], locale) if 'description' in item else '',
                  'datasetId': item['datasetId'],
                  'studyId': item['studyId'],
                  'populationId': item['populationId'] if 'populationId' in item else '',
                  'dceId': item['dceId'] if 'dceId' in item else '',
                  'variableType': item['variableType'],
                  'valueType': item['valueType'] if 'valueType' in item else '',
                  'nature': item['nature'] if 'nature' in item else '',
                  'mimeType': item['mimeType'] if 'mimeType' in item else '',
                  'unit': item['unit'] if 'unit' in item else '',
                  'referencedEntityType': item['referencedEntityType'] if 'referencedEntityType' in item else '',
                  'repeatable': item['repeatable'] if 'repeatable' in item else '',
                  'occurrenceGroup': item['occurrenceGroup'] if 'occurrenceGroup' in item else ''
              }
              if 'categories' in item:
                  row['categories'] = '|'.join([c['name'] for c in item['categories']])
                  row['categories.missing'] = '|'.join([str(c['missing']) for c in item['categories']])
                  row['categories.label'] = '|'.join(map(category_label, item['categories']))
              if 'annotations' in item:
                  for annot in item['annotations']:
                      key = annot['taxonomy'] + '.' + annot['vocabulary']
                      row[key] = annot['value']
              writer.writerow(row)


  @classmethod
  def add_arguments(self, parser):
      '''
      Add tags command specific options

      :param parser - commandline args parser
      '''
      parser.add_argument('--out', '-o', required=False, help='Output file (default is stdout).')
      parser.add_argument('--target', '-t', required=True, choices=['variable', 'dataset', 'study', 'population', 'dce', 'network'],
                          help='Document type to be searched for.')
      parser.add_argument('--query', '-q', required=False, help='Query that filters the documents. If not specified, no filter is applied.')
      parser.add_argument('--start', '-s', required=False, type=int, default=0, help='Start search at document position.')
      parser.add_argument('--limit', '-lm', required=False, type=int, default=100, help='Max number of documents.')
      parser.add_argument('--locale', '-lc', required=False, default='en', help='The language for labels.')

  @classmethod
  def do_command(self, args):
      '''
      Execute search command

      :param args - commandline args
      '''
      service = SearchService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
      if args.target == 'network':
          service.search_networks(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
      elif args.target == 'study':
          self.search_studies(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
      elif args.target == 'population':
          self.search_study_populations(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
      elif args.target == 'dce':
          self.search_study_dces(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
      elif args.target == 'dataset':
          self.search_datasets(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
      elif args.target == 'variable':
          service.search_variables(query=args.query, start=args.start, limit=args.limit, locale=args.locale, out=args.out)
