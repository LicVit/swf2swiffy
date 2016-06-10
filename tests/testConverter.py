import unittest

from swf_data.SwfData import SwfData


class TestConverter(unittest.TestCase):
    def test_main(self):
        swf_file = open('swf/candy.swf', "rb")
        data = swf_file.read()
        swf = SwfData()
        swf.read_data(data)
        print(swf.head)
        for tag in swf.tags:
            print(tag)
