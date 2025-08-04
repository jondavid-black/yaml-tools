import unittest
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../api/python')))
from yasl_py import YASL


class TestYASLPythonAPI(unittest.TestCase):
    def setUp(self):
        self.yasl = YASL()

    def test_process_yasl_basic(self):
        yaml = "foo: bar"
        yasl = "type: object"
        context = {}
        yaml_data = {}
        yasl_data = {}
        result = self.yasl.process_yasl(yaml, yasl, context, yaml_data, yasl_data)
        self.assertTrue(result)

    def test_process_yasl_error(self):
        yaml = ""
        yasl = "type: object"
        context = {}
        yaml_data = {}
        yasl_data = {}
        with self.assertRaises(Exception) as cm:
            result = self.yasl.process_yasl(yaml, yasl, context, yaml_data, yasl_data)
            # TODO What whould we want / expect here?  Is an exception the right thing?

if __name__ == "__main__":
    unittest.main()
