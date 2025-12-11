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

        last_error = None

        def try_status_change():
            nonlocal last_error
            try:
                response = restService.send_request("%s/_status?value=DELETED" % resource, restService.make_request("PUT"))
                return response.code == 204
            except HTTPError as e:
                last_error = e
                # Retry on 404 (resource not indexed yet) or 5xx (server errors)
                if e.code == 404 or e.is_server_error():
                    return False
                raise

        # Retry with exponential backoff - longer timeout in CI
        # Using longer timeout since status changes can take time after import
        timeout = Utils.get_timeout(10)  # 10s local, 30s in CI
        success = Utils.wait_for_condition(try_status_change, timeout=timeout, interval=1, backoff='exponential')
        if not success:
            error_msg = f"Failed to change status to DELETED for {resource}"
            if last_error:
                error_msg += f" - Last error: {last_error.code} {last_error}"
            assert False, error_msg

    def __test_deleteResource(self, restService, resource):
        def try_delete():
            try:
                # Don't fail on errors so we can handle 404 and 409 as retriable
                request = restService.make_request("DELETE").ignore_fail_on_error()
                response = restService.send_request(resource, request)

                # 204 = deleted, 404 = already gone (both success)
                if response.code in (204, 404):
                    return True
                # 409 = conflict (still has dependencies, retry)
                elif response.code == 409:
                    return False
                else:
                    # Unexpected error code, fail immediately
                    assert False, f"Unexpected response {response.code} deleting {resource}: {response.content}"
            except Exception as e:
                assert False, f"Exception while deleting resource {resource}: {e}"

        # Retry delete with exponential backoff for 409 conflicts
        timeout = Utils.get_timeout(15)  # 15s local, 45s in CI
        success = Utils.wait_for_condition(try_delete, timeout=timeout, interval=1, backoff='exponential')
        assert success, f"Failed to delete resource {resource} after {timeout}s (dependencies not cleared)"

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
                                                     restService.make_request("GET")).code == 200,
                    timeout=Utils.get_timeout(10)
                )
                Utils.wait_for_condition(
                    lambda: restService.send_request("/draft/network/dummy-test-network",
                                                     restService.make_request("GET")).code == 200,
                    timeout=Utils.get_timeout(10)
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
                                                 restService.make_request("GET")).code == 200,
                timeout=Utils.get_timeout(10)
            )
            Utils.wait_for_condition(
                lambda: restService.send_request("/draft/network/dummy-test-network",
                                                 restService.make_request("GET")).code == 200,
                timeout=Utils.get_timeout(10)
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
