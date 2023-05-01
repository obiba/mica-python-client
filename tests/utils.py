import sys
from argparse import ArgumentParser
from obiba_mica import MicaClient

class Utils:
  # SERVER = 'https://mica-demo.obiba.org'
  SERVER = 'http://localhost:8082'
  USER = 'administrator'
  PASSWORD = 'password'
  DEFAULT_PARAMS = {"accept": False, "content_type": False, "verbose": False, "method": 'GET'}

  @staticmethod
  def make_client(server=None, user=None, password=None):
    return MicaClient.buildWithAuthentication(server= Utils.SERVER if server is None else server,
                                              user=Utils.USER if user is None else user,
                                              password=Utils.PASSWORD if password is None else password,
                                              otp=None)

  @staticmethod
  def make_arg_parser():
    parser = ArgumentParser()
    parser.add_argument('--mica', '-mk', required=False, help='Mica server base url (default: http://localhost:8082)')
    parser.add_argument('--user', '-u', required=False, help='User name')
    parser.add_argument('--password', '-p', required=False, help='User password')
    parser.add_argument('--otp', '-ot', action='store_true', help='Whether a one-time password is to be provided (required when connecting with username/password AND two-factor authentication is enabled)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    return parser

  @staticmethod
  def parse_arg_values(parser=None, server=None, user=None, password=None, params=[]):

    argv = [
      'test',
      '--mica', Utils.SERVER if server is None else server,
      '--user', Utils.USER if user is None else user,
      '--password', Utils.PASSWORD if password is None else password
    ]

    if params is not None:
      argv = argv + params

    sys.argv = argv
    args = parser.parse_args()

    return args