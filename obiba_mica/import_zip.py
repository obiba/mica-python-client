"""
Import data exported from old mica as zip files.
"""

from obiba_mica.core import MicaClient
import os.path
import os
import tempfile
import zipfile
import re
import json
import shutil


class FileImportService:

    def __init__(self, client: MicaClient, verbose: bool = False):
        self.client = client
        self.verbose = verbose

    def __make_request(self):
        request = self.client.new_request()
        request.method("POST")
        request.fail_on_error()
        request.accept_json()
        if self.verbose:
            request.verbose()
        return request

    def __upgradeStudy(self, study):
        study.pop("obiba.mica.CollectionStudyDto.type", None)
        if "obiba.mica.EntityStateDto.studySummaryState" in study:
            study["state"] = study["obiba.mica.EntityStateDto.studySummaryState"]
        study.pop("obiba.mica.EntityStateDto.studySummaryState", None)

    def __upgradeDataset(self, dataset):
        if "obiba.mica.StudyDatasetDto.type" in dataset:
            dataset["collected"] = dataset["obiba.mica.StudyDatasetDto.type"]
            dataset.pop("obiba.mica.StudyDatasetDto.type", None)
        else:
            dataset["protocol"] = dataset["obiba.mica.HarmonizedDatasetDto.type"]
            dataset.pop("obiba.mica.HarmonizedDatasetDto.type", None)

    def __upgradeZip(self, path):
        """
        Read content of the zip file
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # Extract the original zip file into the temporary directory
            with zipfile.ZipFile(path, "r") as zip_ref:
                zip_ref.extractall(temp_dir)

                # Iterate over each file in the temporary directory
                for root, dirs, files in os.walk(temp_dir):
                    for file_name in files:
                        file_path = os.path.join(root, file_name)

                        res = re.findall(r"(study|dataset)-[^\.]*\.json$", file_name, re.DOTALL)
                        if len(res) > 0:
                            isStudy = res[0] == "study"

                            with open(file_path, mode="r") as f:
                                # Read the content of the file
                                content = json.loads(f.read(), encoding="utf-8")
                                if isStudy:
                                    self.__upgradeStudy(content)
                                else:
                                    self.__upgradeDataset(content)

                            with open(file_path, mode="w") as f:
                                # Write the content back to the file
                                f.write(json.dumps(content))

            upgradedZip = "/tmp/upgraded"
            shutil.make_archive(upgradedZip, "zip", temp_dir)
            return f"{upgradedZip}.zip"

    def import_zip(self, path, publish: bool = None, legacy: bool = False):
        """
        Import the Zip file content

        :param path - local path to the zip file
        :param publish - If True, after the upload, publish the zipped Mica documents (Network, Study, Dataset, files)
        """
        print("Importing {} ...".format(path))

        query = "publish=%s" % str(publish).lower() if publish is not None and publish else ""
        request = self.__make_request()

        if legacy:
            upgradedZip = self.__upgradeZip(path)
            request.content_upload(upgradedZip)
            # remove file
            os.remove(upgradedZip)
        else:
            request.content_upload(path)

        return request.resource("/draft/studies/_import?%s" % query).send()

    @classmethod
    def __printResponse(cls, response):
        res = response.content
        # output to stdout
        if len(res) > 0:
            print(res)

    @classmethod
    def add_arguments(cls, parser):
        """
        Add REST command specific options

        :param parser - commandline args parser
        """
        parser.add_argument("path", help="Path to the zip file or directory that contains zip files to be imported")
        parser.add_argument("--publish", "-pub", action="store_true", help="Publish imported study")
        parser.add_argument("--legacy", "-leg", action="store_true", help="Import legacy entities")

    @classmethod
    def do_command(cls, args):
        """
        Execute Import Zip command

        :param args - commandline args
        """

        service = FileImportService(MicaClient.build(MicaClient.LoginInfo.parse(args)), args.verbose)
        if args.path.endswith(".zip"):
            cls.__printResponse(service.import_zip(args.path, args.publish))
        else:
            for export_file in os.listdir(args.path):
                if export_file.endswith(".zip"):
                    cls.__printResponse(service.import_zip(os.path.join(args.path, export_file), args.publish, args.legacy))
