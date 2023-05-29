from obiba_mica.core import MicaClient
import json

class StudyTableBuilder:

  def __init__(self, studyTable: None):
      self.studyTable = studyTable if studyTable is not None else {}

  def study(self, value):
      self.studyTable['studyId'] = value
      return self

  def population(self, value):
      self.studyTable['populationId'] = value
      return self

  def dce(self, value):
      self.studyTable['dataCollectionEventId'] = value
      return self

  def project(self, value):
      self.studyTable['project'] = value
      return self

  def table(self, value):
      self.studyTable['table'] = value
      return self

  def build(self):
      return self.studyTable

class CollectedDatasetService:
  """
  Update an existing collected dataset, mainly for managing the linkage with opal.
  """

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose

  def new_request(self):
      """
      Creates a MicaRequest instance
      """
      request = self.client.new_request()
      request.fail_on_error()
      request.accept_json()
      if self.verbose:
          request.verbose()
      return request

  def get_dataset(self, id):
      """
      Retrieves a colleted

      :param id - dataset id
      """
      path = '/draft/collected-dataset/' + id
      request = self.new_request()
      response = request.get().resource(path).send()
      return json.loads(response.content)

  def update_study_table(self, dataset, comment=[], study: str = None, population: str = None, dce: str = None, project: str = None, table: str = None):
      """
      Updates the collected datast's study table holding the information to associated Opal Project/Table

      :param dataset - dataset document
      :param comment - commit message
      :param study - dataset's associated study ID
      :param population - dataset's associated population ID
      :param dce - dataset's associated data collection event ID
      :param project - assiociated Opal project name
      :param table - assiociated Opal table name
      """
      dataset.pop('obiba.mica.EntityStateDto.datasetState', None)
      dataset.pop('variableType', None)
      dataset.pop('timestamps', None)
      dataset.pop('published', None)
      dataset.pop('permissions', None)

      if 'obiba.mica.CollectedDatasetDto.type' not in dataset:
          if not study or not population or not dce or not project or not table:
              raise ValueError("Study table is missing and cannot be created.")
          dataset['obiba.mica.CollectedDatasetDto.type'] = {'studyTable': {}}
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
          builder.table(table)

      dataset['obiba.mica.CollectedDatasetDto.type']['studyTable'] = builder.build()

  def update_dataset(self, dataset, comment):
      """
      Sends the updated collected datast to Mica server

      :param dataset - updated dataset document
      :param comment - commit comment
      """
      path = '/draft/collected-dataset/%s' % dataset['id']
      request = self.new_request()
      request.put().resource(path).query({'comment': ', '.join(comment) + ' (update-collected-dataset)'}).content_type_json()
      request.content(json.dumps(dataset, separators=(',', ':')))
      if self.verbose:
          print("Updated: ")
          print(json.dumps(dataset, sort_keys=True, indent=2, separators=(',', ': ')))
      return request.send()

  def update(self, datasetId: str, study: str = None, population: str = None, dce: str = None, project: str = None, table: str = None):
      """
      Updates the collected datast's study table holding the information to associated Opal Project/Table

      :param datasetId - dataset ID
      :param comment - commit message
      :param study - dataset's associated study ID
      :param population - dataset's associated population ID
      :param dce - dataset's associated data collection event ID
      :param project - assiociated Opal project name
      :param table - assiociated Opal table name
      """
      if self.verbose:
          print("Updating %s ..." % datasetId)

      # get existing and remove useless fields
      dataset = self.get_dataset(datasetId)
      comment = []
      self.update_study_table(dataset, comment, study, population, dce, project, table)
      return self.update_dataset(dataset, comment)

  def __publish(self, datasetId: str, method: str = 'PUT'):
    path = '/draft/collected-dataset/%s' % datasetId
    request = self.new_request()
    return request.method(method).resource(path + '/_publish').send()

  def publish(self, datasetId: str):
    """
    Publishs a collected dataset

    :param datasetId - dataset document ID
    """
    return self.__publish(datasetId, 'PUT')

  def unpublish(self, datasetId: str):
    """
    Unpublishes a collected dataset

    :param datasetId - dataset document ID
    """
    return self.__publish(datasetId, 'DELETE')

  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options

      :param parser commandline args parser
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

      :param args - commandline args
      """
      # Build and send request
      service = CollectedDatasetService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)

      if args.project or args.table:
          service.update(args.id, args.study, args.population, args.dce, args.project, args.table)

      if args.publish:
          if args.verbose:
              print("Publishing " + args.id + "...")
          service.publish(args.id)
      elif args.unpublish:
          if args.verbose:
              print("Unpublishing " + args.id + "...")
          service.unpublish(args.id)
