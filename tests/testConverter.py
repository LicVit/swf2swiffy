import unittest

from converter.Converter import Converter


class TestConverter(unittest.TestCase):
    def test_main(self):
        swf_file = open('swf/candy.swf', "rb")
        data = swf_file.read()
        converter = Converter(data)
        swiffy = converter.to_swiffy()
        print(swiffy)
