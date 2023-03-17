"""
Update several existing collected dataset, mainly for managing the linkage with opal.
"""

from obiba_mica.core import MicaClient
import json
import re

class CollectedDatasetsService:

  @classmethod
  def add_arguments(cls, parser):
      """
      Add REST command specific options
      """
      parser.add_argument('id', help='Regular expression to filter the collected dataset IDs')
      parser.add_argument('--project', '-prj', required=False, help='Opal project')
      parser.add_argument('--dry', '-d', action='store_true', help='Dry run to evaluate the regular expression')
      parser.add_argument('--publish', '-pub', action='store_true', help='Publish the colected dataset')
      parser.add_argument('--unpublish', '-un', action='store_true', help='Unpublish the collected dataset')

  @classmethod
  def new_request(cls, args):
      request = MicaClient.build(MicaClient.LoginInfo.parse(args)).new_request()
      request.fail_on_error()
      request.accept_json()
      if args.verbose:
          request.verbose()
      return request

  @classmethod
  def do_update(cls, path, args, id):
      print("Updating " + id + "...")
      # get existing and remove useless fields
      request = cls.new_request(args)
      response = request.get().resource(path).send()
      dataset = json.loads(response.content)
      dataset.pop('obiba.mica.EntityStateDto.datasetState', None)
      dataset.pop('variableType', None)
      dataset.pop('timestamps', None)
      dataset.pop('published', None)
      dataset.pop('permissions', None)
      if 'obiba.mica.CollectedDatasetDto.type' not in dataset:
          raise ValueError("Study table is missing in " + id)
      dataset['obiba.mica.CollectedDatasetDto.type']['studyTable'].pop('studySummary', None)

      # update
      comment = []
      if args.project:
          comment.append('Project: ' + args.project)
          dataset['obiba.mica.CollectedDatasetDto.type']['studyTable']['project'] = args.project
      request = cls.new_request(args)
      request.put().resource(path).query({ 'comment': ', '.join(comment) + ' (update-collected-datasets)' }).content_type_json()
      request.content(json.dumps(dataset, separators=(',',':')))
      if args.verbose:
          print("Updated: ")
          print(json.dumps(dataset, sort_keys=True, indent=2, separators=(',', ': ')))
      request.send()

  @classmethod
  def do_command(cls, args):
      """
      Execute datasets update command
      """
      # Build and send request
      path = '/draft/collected-datasets'
      request = cls.new_request(args)
      response = request.get().resource(path).send()
      datasets = json.loads(response.content)
      for dataset in datasets:
          id = dataset['id']
          if re.match(args.id, id):
              if args.dry:
                  print(id)
              else:
                  path = '/draft/collected-dataset/' + id
                  if args.project:
                      cls.do_update(path, args, id)
                  if args.publish:
                      print("Publishing " + id + "...")
                      request = cls.new_request(args)
                      request.put().resource(path + '/_publish').send()
                  if args.unpublish:
                      print("Unpublishing " + id + "...")
                      request = cls.new_request(args)
                      request.delete().resource(path + '/_publish').send()
