import abc
import os
from unittest import TestCase


class BaseTest(TestCase):
    test_dir = os.path.dirname(__file__)

    @abc.abstractmethod
    def setUp(self):
        raise NotImplementedError

    def tearDown(self):
        print("", flush=True)

    @staticmethod
    def print_header(header):
        header = f"Testing {header}"
        print("#" * len(header))
        print(header)
        print("#" * len(header), flush=True)
