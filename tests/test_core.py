import unittest
from tests.utils import Utils


class TestClass(unittest.TestCase):

    def test_sendRestBadServer(self):
        try:
            Utils.make_client(server="http://deadbeef:8080")
            assert False
        except Exception:
            assert True

    def test_sendRestBadCredentials(self):
        try:
            Utils.make_client(user="admin")
            assert False
        except Exception:
            assert True

    def test_invalidRestCall(self):
        try:
            self.__test_sendRestRequest("/draft/individual-studie")
            assert False
        except Exception:
            assert True
