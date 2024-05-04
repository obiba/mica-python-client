class MicaLegacySupport:

    @staticmethod
    def getNetworkSearchResults(dto):
        """
        Get network search results
        """

        if dto["networkResultDto"] and dto["networkResultDto"]["totalHits"] > 0:
            key = "obiba.mica.NetworkResultDto.result" if "obiba.mica.NetworkResultDto.result" in dto["networkResultDto"] else "networkResult"
            return dto["networkResultDto"][key]["networks"]

        return []

    @staticmethod
    def getStudySearchResults(dto):
        """
        Get study search results
        """

        if dto["studyResultDto"] and dto["studyResultDto"]["totalHits"] > 0:
            key = "obiba.mica.StudyResultDto.result" if "obiba.mica.StudyResultDto.result" in dto["studyResultDto"] else "studyResult"
            return dto["studyResultDto"][key]["summaries"]

        return []

    @staticmethod
    def getDatasetSearchResults(dto):
        """
        Get dataset search results
        """

        if dto["datasetResultDto"] and dto["datasetResultDto"]["totalHits"] > 0:
            key = "obiba.mica.DatasetResultDto.result" if "obiba.mica.DatasetResultDto.result" in dto["datasetResultDto"] else "datasetResult"
            return dto["datasetResultDto"][key]["datasets"]

        return []

    @staticmethod
    def getVariableSearchResults(dto):
        """
        Get variable search results
        """

        if dto["variableResultDto"] and dto["variableResultDto"]["totalHits"] > 0:
            key = "obiba.mica.DatasetVariableResultDto.result" if "obiba.mica.DatasetVariableResultDto.result" in dto["variableResultDto"] else "variableResult"
            return dto["variableResultDto"][key]["summaries"]

        return []

    @staticmethod
    def getDatasetStudyTableInfo(dataset, info):
        """
        Get dataset study table info
        """
        if dataset["variableType"] == "Collected":
            key = "obiba.mica.CollectedDatasetDto.type" if "obiba.mica.CollectedDatasetDto.type" in dataset else "collected"
            info["study_id"] = dataset[key]["studyTable"]["studyId"]
            info["population_id"] = dataset[key]["studyTable"]["populationId"]
            info["dce_id"] = dataset[key]["studyTable"]["dceId"]
        else:
            key = "obiba.mica.HarmonizedDatasetDto.type" if "obiba.mica.HarmonizedDatasetDto.type" in dataset else "protocol"
            info["study_id"] = dataset[key]["harmonizationTable"]["studyId"]
            info["population_id"] = ""
            info["dce_id"] = ""

    @staticmethod
    def removeDatasetEntityState(dataset):
        dataset.pop('obiba.mica.EntityStateDto.datasetState', None)
        dataset.pop('state', None)

    @staticmethod
    def getCollectedDataset(dataset):
        key = "obiba.mica.CollectedDatasetDto.type" if "obiba.mica.CollectedDatasetDto.type" in dataset else "collected"
        return dataset[key] if key in dataset else None
