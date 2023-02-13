#
# Mica commands main entry point
#
import argparse
import sys

import obiba_mica.file as file
import obiba_mica.rest as rest
import obiba_mica.import_zip as import_zip
import obiba_mica.perm_network as perm_network
import obiba_mica.perm_project as perm_project
import obiba_mica.perm_individual_study as perm_individual_study
import obiba_mica.perm_harmonization_study as perm_harmonization_study
import obiba_mica.perm_collected_dataset as perm_collected_dataset
import obiba_mica.perm_harmonized_dataset as perm_harmonized_dataset
import obiba_mica.access_network as access_network
import obiba_mica.access_project as access_project
import obiba_mica.access_individual_study as access_individual_study
import obiba_mica.access_harmonization_study as access_harmonization_study
import obiba_mica.access_collected_dataset as access_collected_dataset
import obiba_mica.access_harmonized_dataset as access_harmonized_dataset
import obiba_mica.access_file as access_file
import obiba_mica.search as search
import obiba_mica.plugin as plugin
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
                  import_zip.add_arguments, import_zip.do_command)
    add_subcommand(subparsers, 'file', 'Mica file system actions, for advanced users.', file.add_arguments,
                  file.do_command)

    add_subcommand(subparsers, 'perm-network', 'Apply permission on a network.',
                  perm_network.add_arguments, perm_network.do_command)
    add_subcommand(subparsers, 'perm-project', 'Apply permission on a research project.',
                  perm_project.add_arguments, perm_project.do_command)
    add_subcommand(subparsers, 'perm-individual-study', 'Apply permission on an individual study.',
                  perm_individual_study.add_arguments, perm_individual_study.do_command)
    add_subcommand(subparsers, 'perm-harmonization-study', 'Apply permission on a harmonization study.',
                  perm_harmonization_study.add_arguments, perm_harmonization_study.do_command)
    add_subcommand(subparsers, 'perm-collected-dataset', 'Apply permission on a collected dataset.',
                  perm_collected_dataset.add_arguments, perm_collected_dataset.do_command)
    add_subcommand(subparsers, 'perm-harmonized-dataset', 'Apply permission on a harmonized dataset.',
                  perm_harmonized_dataset.add_arguments, perm_harmonized_dataset.do_command)

    add_subcommand(subparsers, 'access-network', 'Apply access on a network.',
                  access_network.add_arguments, access_network.do_command)
    add_subcommand(subparsers, 'access-project', 'Apply access on a research project.',
                  access_project.add_arguments, access_project.do_command)
    add_subcommand(subparsers, 'access-individual-study', 'Apply access on an individual study.',
                  access_individual_study.add_arguments, access_individual_study.do_command)
    add_subcommand(subparsers, 'access-harmonization-study', 'Apply access on a harmonization study.',
                  access_harmonization_study.add_arguments, access_harmonization_study.do_command)
    add_subcommand(subparsers, 'access-collected-dataset', 'Apply access on a collected dataset.',
                  access_collected_dataset.add_arguments, access_collected_dataset.do_command)
    add_subcommand(subparsers, 'access-harmonized-dataset', 'Apply access on a harmonized dataset.',
                  access_harmonized_dataset.add_arguments, access_harmonized_dataset.do_command)
    add_subcommand(subparsers, 'access-file', 'Apply access on a file.',
                  access_file.add_arguments, access_file.do_command)

    add_subcommand(subparsers, 'search', 'Perform a search query on variables, datasets, studies (including populations and data collection events) and networks.', search.add_arguments,
                  search.do_command)

    add_subcommand(subparsers, 'tags', 'Extract classification tags from published variables.', tags.add_arguments,
                  tags.do_command)

    add_subcommand(subparsers, 'update-collected-dataset', 'Update collected dataset linkage with an Opal table.', update_collected_dataset.add_arguments,
                  update_collected_dataset.do_command)
    add_subcommand(subparsers, 'update-collected-datasets', 'Update collected datasets linkage with an Opal table.', update_collected_datasets.add_arguments,
                  update_collected_datasets.do_command)

    add_subcommand(subparsers, 'plugin', 'Manage system plugins.', plugin.add_arguments,
                  plugin.do_command)

    add_subcommand(subparsers, 'rest', 'Request directly the Mica REST API, for advanced users.', rest.add_arguments,
                  rest.do_command)

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
