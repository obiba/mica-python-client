import unittest
from obiba_mica.import_zip import FileImportService
from obiba_mica.rest import RestService
from tests.utils import Utils


class TestClass(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        cls.client = Utils.make_client()
        cls.needsLegacySupport = FileImportService.needsLegacySupport(cls.client)

    def __test_changeResourceStatusToDelete(self, restService, resource):
        from obiba_mica.core import HTTPError

        def try_status_change():
            try:
                response = restService.send_request("%s/_status?value=DELETED" % resource, restService.make_request("PUT"))
                return response.code == 204
            except HTTPError as e:
                # Retry on server errors (5xx) - resource might not be ready yet
                if e.is_server_error():
                    return False
                raise

        # Retry with exponential backoff - longer timeout in CI
        timeout = Utils.get_timeout(7)  # 7s local, 21s in CI
        success = Utils.wait_for_condition(try_status_change, timeout=timeout, interval=1, backoff='exponential')
        assert success, f"Failed to change status to DELETED for {resource}"

    def __test_deleteResource(self, restService, resource):
        try:
            # Don't fail on errors so we can handle 404 as valid (idempotent delete)
            request = restService.make_request("DELETE").ignore_fail_on_error()
            response = restService.send_request(resource, request)
            # Accept 204 (deleted) or 404 (already gone) to make the test idempotent
            assert response.code in (204, 404), f"Failed to delete resource {resource}: {response.content}"
        except Exception as e:
            assert False, f"Exception while deleting resource {resource}: {e}"

    def test_1_importZip(self):
        try:
            if not self.needsLegacySupport:
                service = FileImportService(self.client)
                response = service.import_zip("./tests/resources/dummy-test-study.zip", True)
                assert response.code == 200

                # Wait for resources to be indexed/available after import
                restService = RestService(self.client)
                Utils.wait_for_condition(
                    lambda: restService.send_request("/draft/individual-study/dummy-test-study",
                                                     restService.make_request("GET")).code == 200
                )
                Utils.wait_for_condition(
                    lambda: restService.send_request("/draft/network/dummy-test-network",
                                                     restService.make_request("GET")).code == 200
                )
            else:
                assert True
        except Exception as e:
            assert False

    def test_2_deleteDummy(self):
        try:
            if not self.needsLegacySupport:
                restService = RestService(self.client)
                self.__test_changeResourceStatusToDelete(restService, "/draft/network/dummy-test-network")
                self.__test_deleteResource(restService, "/draft/network/dummy-test-network")
                self.__test_changeResourceStatusToDelete(restService, "/draft/individual-study/dummy-test-study")
                self.__test_deleteResource(restService, "/draft/individual-study/dummy-test-study")
            else:
                assert True
        except Exception as e:
            assert False

    def test_3_importZip(self):
        try:
            service = FileImportService(self.client)
            response = service.import_zip("./tests/resources/dummy-test-study-legacy.zip", True, True)
            assert response.code == 200

            # Wait for resources to be indexed/available after import
            restService = RestService(self.client)
            Utils.wait_for_condition(
                lambda: restService.send_request("/draft/individual-study/dummy-test-study",
                                                 restService.make_request("GET")).code == 200
            )
            Utils.wait_for_condition(
                lambda: restService.send_request("/draft/network/dummy-test-network",
                                                 restService.make_request("GET")).code == 200
            )
        except Exception as e:
            assert False

    def test_4_deleteDummy(self):
        try:
            restService = RestService(self.client)
            self.__test_changeResourceStatusToDelete(restService, "/draft/network/dummy-test-network")
            self.__test_deleteResource(restService, "/draft/network/dummy-test-network")
            self.__test_changeResourceStatusToDelete(restService, "/draft/individual-study/dummy-test-study")
            self.__test_deleteResource(restService, "/draft/individual-study/dummy-test-study")
        except Exception as e:
            assert False
