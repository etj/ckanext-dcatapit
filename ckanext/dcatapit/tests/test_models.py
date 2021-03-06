import os
import json

import unittest
import nose

from ckan.model import Session
from ckan.plugins import toolkit

try:
    from ckan.tests import helpers
except ImportError:
    from ckan.new_tests import helpers

from ckanext.dcatapit.model.license import (load_from_graph, 
    License, LocalizedLicenseName, _get_graph, SKOS)

def get_path(fname):
    return os.path.join(os.path.dirname(__file__),
                        '..', '..', '..', 'examples', fname)

class LicenseTestCase(unittest.TestCase):
    def setUp(self):

        self.licenses = get_path('licenses.rdf')
        self.g = _get_graph(path=self.licenses)

    def test_licenses(self):

        load_from_graph(path=self.licenses)
        Session.flush()

        all_licenses = License.q()
        count = all_licenses.count()
        self.assertTrue(count> 0)
        self.assertTrue(count == len(list(self.g.subjects(None, SKOS.Concept))))
        
        all_localized = LocalizedLicenseName.q()
        self.assertTrue(all_localized.count() > 0)

        for_select = License.for_select('it')
        
        # check license type
        self.assertTrue(all([s[0] for s in for_select]))


    def test_tokenizer(self):

        load_from_graph(path=self.licenses)
        Session.flush()
        tokens = License.get_as_tokens()
        self.assertTrue(len(tokens.keys())>0)

        from_token, default = License.find_by_token('cc-by-sa')
        self.assertFalse(default)
        self.assertTrue(from_token)
        self.assertTrue('ccbysa' in from_token.uri.lower())

        from_token, default = License.find_by_token('cc-zero') #http://opendefinition.org/licenses/cc-zero/')
        self.assertFalse(default)
        self.assertTrue(from_token)

        self.assertTrue('PublicDomain' in from_token.license_type)
        
        from_token, default = License.find_by_token('Creative Commons Attribuzione') #http://opendefinition.org/licenses/cc-zero/')
        self.assertFalse(default)
        self.assertTrue(from_token)

        self.assertTrue('Attribution' in from_token.license_type)

        odbl = """["Open Data Commons Open Database License / OSM (ODbL/OSM): You are free to copy, distribute, transmit and adapt our data, as long as you credit OpenStreetMap and its contributors\nIf you alter or build upon our data, you may distribute the result only under the same licence. (http://www.openstreetmap.org/copyright)"]"""

        from_token, default = License.find_by_token(odbl, 'other')
        self.assertFalse(default)
        self.assertTrue(from_token)
        self.assertTrue('odbl' in from_token.default_name.lower())


    def tearDown(self):
        Session.rollback()
