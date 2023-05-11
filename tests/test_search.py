import unittest
from obiba_mica.search import SearchService
from obiba_mica.core import HTTPError
from tests.utils import Utils
from io import StringIO, BytesIO
import sys

class TestClass(unittest.TestCase):

  @classmethod
  def setup_class(cls):
    cls.service = SearchService(Utils.make_client())

  def test_searchNetworks(self):
    try:
      output = StringIO()
      self.service.search_networks(query='network(in(id,bioshare-eu))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'bioshare-eu' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchStudies(self):
    try:
      output = StringIO()
      self.service.search_studies(query='study(in(id,cls))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'cls' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchInitiatives(self):
    try:
      output = StringIO()
      self.service.search_initiatives(query='study(in(id,cptp-hs))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'cptp-hs' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchStudyPopulations(self):
    try:
      output = StringIO()
      self.service.search_study_populations(query='study(in(id,cls))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'cls:1' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchStudyDces(self):
    try:
      output = StringIO()
      self.service.search_study_dces(query='study(in(id,cls))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'cls:1:1' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False


  def test_searchDatasets(self):
    try:
      output = StringIO()
      self.service.search_datasets(query='dataset(in(id,cls-wave1))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'cls-wave1' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchProtocols(self):
    try:
      output = StringIO()
      self.service.search_datasets(query='dataset(in(id,chpt-generic-ds))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'chpt-generic-ds' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False

  def test_searchVariables(self):
    try:
      output = StringIO()
      self.service.search_variables(query='variable(in(Mlstr_area.Lifestyle_behaviours,(Alcohol)))', out=output)
      response = output.getvalue()
      if len(response) > 0 and 'Alcohol' in response:
        assert True
      else:
        assert False

    except Exception as e:
      assert False