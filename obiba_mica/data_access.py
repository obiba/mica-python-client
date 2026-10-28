"""
Mica data access requests management.
"""

import sys
import csv
import json
from obiba_mica.core import MicaClient, UriBuilder


class DataAccessService:
    """
    Service listing the data access requests visible to the user, with the same information as the 'My Data Access' page
    (title, status, dates, preliminary and amendments/feasibilities/agreements counts).
    """

    FIELDNAMES = [
        "id",
        "applicant",
        "title",
        "status",
        "archived",
        "lastUpdate",
        "submitDate",
        "approvedDate",
        "preliminaryStatus",
        "totalAmendments",
        "pendingAmendments",
        "totalFeasibilities",
        "pendingFeasibilities",
        "totalAgreements",
        "pendingAgreements",
    ]

    # child entities with one of these statuses are not pending
    CLOSED_STATUSES = ("APPROVED", "REJECTED")

    def __init__(self, client: MicaClient, verbose: bool = False):
        self.client = client
        self.verbose = verbose

    def __make_request(self):
        request = self.client.new_request()
        request.fail_on_error()
        request.accept_json()
        if self.verbose:
            request.verbose()
        return request

    def __get(self, path: list, params: dict = None):
        request = self.__make_request().get().resource(UriBuilder(path, {}).build())
        if params:
            request.query(params)
        return request.send().as_json()

    def is_preliminary_enabled(self) -> bool:
        """
        Whether the data access preliminary form is enabled
        """
        config = self.__get(["config", "data-access"])
        return bool(config and config.get("preliminaryEnabled", False))

    def list_requests(self, status: list = None) -> list:
        """
        Lists the data access requests the user is permitted to view, optionally filtered by status

        :param status - list of request statuses
        """
        requests = self.__get(["data-access-requests"], {"status": status} if status else None)
        return requests if requests else []

    def list_children(self, id: str, children: str) -> list:
        """
        Lists the child entities of a data access request

        :param id - data access request ID
        :param children - one of 'amendments', 'feasibilities' or 'agreements'
        """
        entities = self.__get(["data-access-request", id, children])
        return entities if entities else []

    def get_preliminary(self, id: str):
        """
        Gets the preliminary of a data access request (note: Mica creates it if it does not exist yet)

        :param id - data access request ID
        """
        return self.__get(["data-access-request", id, "prelim"])

    def __counts(self, entities: list):
        pending = [e for e in entities if e.get("status") not in self.CLOSED_STATUSES]
        return len(entities), len(pending)

    def __last_status_date(self, request: dict, status: str):
        # date of the last change to the given status
        for change in reversed(request.get("statusChangeHistory", [])):
            if change.get("to") == status:
                return change.get("changedOn")
        return None

    def list_bundles(self, status: list = None) -> list:
        """
        Lists the data access requests with their preliminary and child entities counts

        :param status - list of request statuses
        """
        requests = self.list_requests(status)
        preliminary_enabled = self.is_preliminary_enabled() if requests else False

        bundles = []
        for request in requests:
            id = request["id"]
            preliminary = self.get_preliminary(id) if preliminary_enabled else None
            title = request.get("title")
            if not title and preliminary:
                title = preliminary.get("title")
            total_amendments, pending_amendments = self.__counts(self.list_children(id, "amendments"))
            total_feasibilities, pending_feasibilities = self.__counts(self.list_children(id, "feasibilities"))
            total_agreements, pending_agreements = self.__counts(self.list_children(id, "agreements"))
            bundles.append({
                "id": id,
                "applicant": request.get("applicant"),
                "title": title if title else "",
                "status": request.get("status"),
                "archived": request.get("archived", False),
                "lastUpdate": request.get("timestamps", {}).get("lastUpdate"),
                "submitDate": self.__last_status_date(request, "SUBMITTED"),
                "approvedDate": self.__last_status_date(request, "APPROVED"),
                "preliminaryStatus": preliminary.get("status") if preliminary else None,
                "totalAmendments": total_amendments,
                "pendingAmendments": pending_amendments,
                "totalFeasibilities": total_feasibilities,
                "pendingFeasibilities": pending_feasibilities,
                "totalAgreements": total_agreements,
                "pendingAgreements": pending_agreements,
            })
        return bundles

    @classmethod
    def add_arguments(cls, parser):
        """
        Add data access command specific options

        :param parser - commandline args parser
        """
        parser.add_argument(
            "--status",
            "-st",
            action="append",
            required=False,
            help="Filter by request status (OPENED, SUBMITTED, REVIEWED, CONDITIONALLY_APPROVED, APPROVED, REJECTED), can be repeated",
        )
        parser.add_argument("--out", "-o", required=False, help="Output file (default is stdout)")
        parser.add_argument("--json", "-j", action="store_true", help="Output as JSON instead of CSV")

    @classmethod
    def do_command(cls, args):
        """
        Execute data access command

        :param args - commandline args
        """
        client = MicaClient.build(MicaClient.LoginInfo.parse(args))
        try:
            service = DataAccessService(client, args.verbose)
            status = [s.upper() for s in args.status] if args.status else None
            bundles = service.list_bundles(status)

            if args.out:
                with open(args.out, "w") as file:
                    cls.write_bundles(bundles, file, args.json)
            else:
                cls.write_bundles(bundles, sys.stdout, args.json)
        finally:
            client.close()

    @classmethod
    def write_bundles(cls, bundles: list, file, asJson: bool = False):
        """
        Writes the data access requests bundles as CSV or JSON

        :param bundles - data access requests bundles
        :param file - output file
        :param asJson - if True, JSON is written instead of CSV
        """
        if asJson:
            file.write(json.dumps(bundles, indent=2))
            file.write("\n")
        else:
            writer = csv.DictWriter(file, fieldnames=cls.FIELDNAMES, quoting=csv.QUOTE_ALL)
            writer.writeheader()
            writer.writerows(bundles)
