import sys
import time
import os
from argparse import ArgumentParser
from obiba_mica import MicaClient

class Utils:
  SERVER = 'https://mica-demo.obiba.org'
#   SERVER = 'http://localhost:8082'
  USER = 'administrator'
  PASSWORD = 'password'
  DEFAULT_PARAMS = {"accept": False, "content_type": False, "verbose": False, "method": 'GET'}

  @staticmethod
  def is_ci_environment():
    """
    Detect if running in CI environment (GitHub Actions, etc.)
    Returns True if CI environment variables are set
    """
    return os.getenv('CI', '').lower() == 'true' or os.getenv('GITHUB_ACTIONS', '').lower() == 'true'

  @staticmethod
  def get_timeout(base_timeout):
    """
    Get timeout adjusted for CI environment.
    CI environments are slower, so use 3x the base timeout.

    :param base_timeout - base timeout in seconds for local development
    :return adjusted timeout (base * 3 if CI, else base)
    """
    return base_timeout * 3 if Utils.is_ci_environment() else base_timeout

  @staticmethod
  def make_client(server=None, user=None, password=None):
    return MicaClient.buildWithAuthentication(server= Utils.SERVER if server is None else server,
                                              user=Utils.USER if user is None else user,
                                              password=Utils.PASSWORD if password is None else password,
                                              otp=None)

  @staticmethod
  def wait_for_condition(resource_callback, timeout=10, interval=1, backoff='fixed'):
    """
    Poll until a condition is met or timeout occurs.
    Useful for CI environments where server processing may be slower after write operations.

    :param resource_callback - callable that returns True when resource is ready, False otherwise
    :param timeout - maximum time to wait in seconds (default: 10)
    :param interval - base polling interval in seconds (default: 1)
    :param backoff - backoff strategy: 'fixed' or 'exponential' (default: 'fixed')
                     For exponential: sleeps interval * 2^attempt (1s, 2s, 4s, 8s, ...)
    :return True if condition met, False if timeout

    Example usage (fixed interval):
      Utils.wait_for_condition(
        lambda: restService.send_request('/draft/study/id', restService.make_request('GET')).code == 200
      )

    Example usage (exponential backoff for retries):
      Utils.wait_for_condition(
        lambda: service.publish(id).code == 204,
        timeout=10,
        interval=1,
        backoff='exponential'
      )
    """
    elapsed = 0
    attempt = 0
    while elapsed < timeout:
      try:
        if resource_callback():
          return True
      except Exception:
        # Condition not met yet, keep waiting
        pass

      # Calculate sleep time based on backoff strategy
      if backoff == 'exponential':
        sleep_time = interval * (2 ** attempt)
      else:
        sleep_time = interval

      time.sleep(sleep_time)
      elapsed += sleep_time
      attempt += 1
    return False

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