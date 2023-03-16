#
# Mica commands main entry point
#
import argparse
import sys

from obiba_mica.system import PluginService, RESTService
from obiba_mica.file import FileService
from obiba_mica.access import ProjectAccessService, NetworkAccessService, IndividualStudyAccessService, HarmonizationInitiativeAccessService, CollectedDatasetAccessService, HarmonizationProtocolAccessService, FileAccessService
from obiba_mica.perm import ProjectPermissionService, NetworkPermissionService, HarmonizationInitiativePermissionService, HarmonizationProtocolPermissionService, IndividualStudyPermissionService, CollectedDatasetPermissionService
from obiba_mica.import_zip import FileImportService
from obiba_mica.search import SearchService

import obiba_mica.tags as tags
import obiba_mica.update_collected_dataset as update_collected_dataset
import obiba_mica.update_collected_datasets as update_collected_datasets

def add_mica_arguments(parser):
    """
    Add Mica access arguments
    """
    parser.add_argument('--mica', '-mk', required=False, default='http://localhost:8082', help='Mica server base url (default: http://localhost:8082)')
    parser.add_argument('--user', '-u', required=False, help='User name')
    parser.add_argument('--password', '-p', required=False, help='User password')
    parser.add_argument('--otp', '-ot', action='store_true', help='Whether a one-time password is to be provided (required when connecting with username/password AND two-factor authentication is enabled)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')


def add_subcommand(subparsers, name, help, add_args_func, default_func):
    """
    Make a sub-parser, add default arguments to it, add sub-command arguments and set the sub-command callback function.
    """
    subparser = subparsers.add_parser(name, help=help)
    add_mica_arguments(subparser)
    add_args_func(subparser)
    subparser.set_defaults(func=default_func)


def run():
    """
    Command-line entry point.
    """

    # Parse arguments
    parser = argparse.ArgumentParser(description='Mica command line tool.')
    subparsers = parser.add_subparsers(title='sub-commands',
                                      help='Available sub-commands. Use --help option on the sub-command '
                                            'for more details.')

    # Add subcommands
    add_subcommand(subparsers, 'import-zip', 'Import data from zip file(s) that have been extracted from old Mica',
                  FileImportService.add_arguments, FileImportService.do_command)
    add_subcommand(subparsers, 'file', 'Mica file system actions, for advanced users.', FileService.add_arguments,
                  FileService.do_command)
    add_subcommand(subparsers, 'perm-network', 'Apply permission on a network.',
                  NetworkPermissionService.add_arguments, NetworkPermissionService.do_command)
    add_subcommand(subparsers, 'perm-project', 'Apply permission on a research project.',
                  ProjectPermissionService.add_arguments, ProjectPermissionService.do_command)
    add_subcommand(subparsers, 'perm-individual-study', 'Apply permission on an individual study.',
                  IndividualStudyPermissionService.add_arguments, IndividualStudyPermissionService.do_command)
    add_subcommand(subparsers, 'perm-harmonization-initiative', 'Apply permission on a harmonization initiative.',
                  HarmonizationInitiativePermissionService.add_arguments, HarmonizationInitiativePermissionService.do_command)
    add_subcommand(subparsers, 'perm-collected-dataset', 'Apply permission on a collected dataset.',
                  CollectedDatasetPermissionService.add_arguments, CollectedDatasetPermissionService.do_command)
    add_subcommand(subparsers, 'perm-harmonization-protocol', 'Apply permission on a harmonization protocol.',
                  HarmonizationProtocolPermissionService.add_arguments, HarmonizationProtocolPermissionService.do_command)

    add_subcommand(subparsers, 'access-network', 'Apply access on a network.',
                  NetworkAccessService.add_arguments, NetworkAccessService.do_command)
    add_subcommand(subparsers, 'access-project', 'Apply access on a research project.',
                  ProjectAccessService.add_arguments, ProjectAccessService.do_command)
    add_subcommand(subparsers, 'access-individual-study', 'Apply access on an individual study.',
                  IndividualStudyAccessService.add_arguments, IndividualStudyAccessService.do_command)
    add_subcommand(subparsers, 'access-harmonization-initiative', 'Apply access on a harmonization initiative.',
                  HarmonizationInitiativeAccessService.add_arguments, HarmonizationInitiativeAccessService.do_command)
    add_subcommand(subparsers, 'access-collected-dataset', 'Apply access on a collected dataset.',
                  CollectedDatasetAccessService.add_arguments, CollectedDatasetAccessService.do_command)
    add_subcommand(subparsers, 'access-harmonization-protocol', 'Apply access on a harmonization protocol.',
                  HarmonizationProtocolAccessService.add_arguments, HarmonizationProtocolAccessService.do_command)
    add_subcommand(subparsers, 'access-file', 'Apply access on a file.',
                  FileAccessService.add_arguments, FileAccessService.do_command)

    add_subcommand(subparsers, 'search', 'Perform a search query on variables, datasets, studies (including populations and data collection events) and networks.', SearchService.add_arguments,
                  SearchService.do_command)

    # add_subcommand(subparsers, 'tags', 'Extract classification tags from published variables.', tags.add_arguments,
    #               tags.do_command)

    # add_subcommand(subparsers, 'update-collected-dataset', 'Update collected dataset linkage with an Opal table.', update_collected_dataset.add_arguments,
    #               update_collected_dataset.do_command)
    # add_subcommand(subparsers, 'update-collected-datasets', 'Update collected datasets linkage with an Opal table.', update_collected_datasets.add_arguments,
    #               update_collected_datasets.do_command)

    # add_subcommand(subparsers, 'plugin', 'Manage system plugins.', PluginService.add_arguments,
    #               PluginService.do_command)

    # add_subcommand(subparsers, 'rest', 'Request directly the Mica REST API, for advanced users.', RESTService.add_arguments,
    #               RESTService.do_command)

    # Execute selected command
    args = parser.parse_args()
    if hasattr(args, 'func'):
        try:
            args.func(args)
        except Exception as e:
            print(e)
            sys.exit(2)
    else:
      print('Mica command line tool.')
      print('For more details: mica --help')
