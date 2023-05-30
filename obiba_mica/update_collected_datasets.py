from obiba_mica.core import MicaClient
from obiba_mica.update_collected_dataset import CollectedDatasetService
import json
import re

class CollectedDatasetsService:
  """
  Update several existing collected dataset, mainly for managing the linkage with opal.
  """

  def __init__(self, client: MicaClient, verbose: bool = False):
     self.client = client
     self.verbose = verbose
     self.datasetService = CollectedDatasetService(client, verbose)

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

  def update(self, datasetId: str, project: str):
      """
      Updates a collecetd dataset's Opal project name

      :param datasetId - dataset document ID
      :param project - Opal project name
      """
      return self.datasetService.update(datasetId, project=project)

  def publish(self, datasetId: str):
      """
      Publishes a collected dataset
      """
      return self.datasetService.publish(datasetId)

  def unpublish(self, datasetId: str):
      return self.datasetService.unpublish(datasetId)

  def get_dataset(self, id: str):
      return self.datasetService.get_dataset(id)

  def get_datasets(self, pattern: str):
      """
      Retrieves all collected datasets of a Mica server matching the regular expression pattern

      :param pattern - regular expression pattern
      """
      path = '/draft/collected-datasets'
      request = self.new_request()
      response = request.get().resource(path).send()
      datasets = json.loads(response.content)

      return list(filter(lambda dataset: re.match(pattern, dataset['id']), datasets))

  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options

      :param parser - commandline args parser
      """
      parser.add_argument('id', help='Regular expression to filter the collected dataset IDs')
      parser.add_argument('--project', '-prj', required=False, help='Opal project')
      parser.add_argument('--dry', '-d', action='store_true', help='Dry run to evaluate the regular expression')
      parser.add_argument('--publish', '-pub', action='store_true', help='Publish the colected dataset')
      parser.add_argument('--unpublish', '-un', action='store_true', help='Unpublish the collected dataset')

  @classmethod
  def do_command(cls, args):
      """
      Execute datasets update command

      :param args - commandline args
      """
      # Build and send request
      datasetsService = CollectedDatasetsService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
      datasets = datasetsService.get_datasets(args.id)

      for dataset in datasets:
          id = dataset['id']
          if args.dry:
              print(id)
          else:
              if args.project:
                  datasetsService.update(id, args.project)
              if args.publish:
                  if args.verbose:
                    print("Publishing " + id + "...")
                  datasetsService.publish(id)
              elif args.unpublish:
                  if args.verbose:
                    print("Unpublishing " + id + "...")
                  datasetsService.unpublish(id)
