from objectname import get_target_obj_name
from contextlib import contextmanager
import logging
import unittest


logger = logging.getLogger()
logger.setLevel(logging.INFO)


class TestStringMethods(unittest.TestCase):

    def test_target_obj_name_in_simple_format(self):
        target_name = get_target_obj_name("any-object-name")
        self.assertEqual(target_name, 'any-object-name_processed')

    def test_target_obj_name_in_file_format(self):
        target_name = get_target_obj_name("file.txt")
        self.assertEqual(target_name, 'file_processed.txt')

    def test_target_obj_name_in_path(self):
        target_name = get_target_obj_name("incoming/file.txt")
        self.assertEqual(target_name, 'incoming/file_processed.txt')

            