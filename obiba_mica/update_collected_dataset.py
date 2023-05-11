"""
Update an existing collected dataset, mainly for managing the linkage with opal.
"""

from obiba_mica.core import MicaClient
import json

class StudyTableBuilder:

    def __init__(self, table: None):
        self = table if table is not None else {}

    def study(self, value):
        self['studyId'] = value
        return self

    def population(self, value):
        self['populationId'] = value
        return self

    def dce(self, value):
        self['dataCollectionEventId'] = value
        return self

    def project(self, value):
        self['project'] = value
        return self

    def table(self, value):
        self['table'] = value
        return self
    
    def build(self):
        return self.table

class CollectedDatasetService:
  
  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def new_request(self):
      request = self.client.new_request()
      request.fail_on_error()
      request.accept_json()
      if self.verbose:
          request.verbose()
      return request
  
  def get_dataset(self, id):
      path = '/draft/collected-dataset/' + id
      request = self.new_request()
      response = request.get().resource(path).send()
      return json.loads(response.content)   
  
  def update_study_table(self, dataset, comment = [], study: str = None, population: str = None, dce: str = None, project: str = None, table: str = None):
      dataset.pop('obiba.mica.EntityStateDto.datasetState', None)
      dataset.pop('variableType', None)
      dataset.pop('timestamps', None)
      dataset.pop('published', None)
      dataset.pop('permissions', None)
      
      if 'obiba.mica.CollectedDatasetDto.type' not in dataset:
          if not study or not population or not dce or not project or not table:
              raise ValueError("Study table is missing and cannot be created.")
          dataset['obiba.mica.CollectedDatasetDto.type'] = { 'studyTable': { } }
      dataset['obiba.mica.CollectedDatasetDto.type']['studyTable'].pop('studySummary', None)

      builder = StudyTableBuilder(dataset['obiba.mica.CollectedDatasetDto.type']['studyTable'])

      # update
      comment = []
      if study:
          comment.append('Study: ' + study)
          builder.study(study)
      if population:
          comment.append('Population: ' + population)
          builder.population(population)
      if dce:
          comment.append('DCE: ' + dce)
          builder.dce(dce)
      if project:
          comment.append('Project: ' + project)
          builder.project(project)
      if table:
          comment.append('Table: ' + table)
          builder.table9(table)

      dataset['obiba.mica.CollectedDatasetDto.type']['studyTable'] = builder.build()   

  def update_dataset(self, dataset, comment):
      path = '/draft/collected-dataset/' + dataset.id
      request = self.new_request()
      request.put().resource(path).query({ 'comment': ', '.join(comment) + ' (update-collected-dataset)' }).content_type_json()
      request.content(json.dumps(dataset, separators=(',',':')))
      if self.verbose:
          print("Updated: ")
          print(json.dumps(dataset, sort_keys=True, indent=2, separators=(',', ': ')))
      request.send()

  def do_update(self, path, datasetId: str, study: str = None, population: str = None, dce: str = None, project: str = None, table: str = None):
      print("Updating " + datasetId + "...")
      # get existing and remove useless fields
      dataset = self.get_dataset(datasetId, path)
      comment = []
      self.update_study_table(dataset, comment, study, population, dce, project, table)

      request = self.new_request()
      request.put().resource(path).query({ 'comment': ', '.join(comment) + ' (update-collected-dataset)' }).content_type_json()
      request.content(json.dumps(dataset, separators=(',',':')))
      if self.verbose:
          print("Updated: ")
          print(json.dumps(dataset, sort_keys=True, indent=2, separators=(',', ': ')))
      request.send()

  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options
      """
      parser.add_argument('id', help='Collected dataset ID')
      parser.add_argument('--study', '-std', required=False, help='Mica study')
      parser.add_argument('--population', '-pop', required=False, help='Mica population')
      parser.add_argument('--dce', '-dce', required=False, help='Mica study population data collection event')
      parser.add_argument('--project', '-prj', required=False, help='Opal project')
      parser.add_argument('--table', '-tbl', required=False, help='Opal table')
      parser.add_argument('--publish', '-pub', action='store_true', help='Publish the colected dataset')
      parser.add_argument('--unpublish', '-un', action='store_true', help='Unpublish the collected dataset')

  @classmethod
  def do_command(cls, args):
      """
      Execute dataset update command
      """
      # Build and send request
      service = CollectedDatasetService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
      path = '/draft/collected-dataset/' + args.id
      if args.project or args.table:
          service.do_update(path, args)

      if args.publish:
          print("Publishing " + args.id + "...")
          request = cls.new_request(args)
          request.put().resource(path + '/_publish').send()

      if args.unpublish:
          print("Unpublishing " + args.id + "...")
          request = cls.new_request(args)
          request.delete().resource(path + '/_publish').send()
