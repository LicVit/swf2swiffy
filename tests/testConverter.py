import unittest
import swf_data.SwfData as SwfData

from converter.Converter import Converter


class TestConverter(unittest.TestCase):
    def test_main(self):
        swf_file = open('swf/gacha160611_pet_android.swf', "rb")
        data = swf_file.read()
        converter = Converter(data)
        json = converter.to_swiffy()
        html = converter.to_html()
        html_file = open('html/gacha160611_pet_android.html', 'w')
        html_file.write(html)
        html_file.close()
        json_file = open('html/gacha160611_pet_android.json', 'w')
        json_file.write(json)
        json_file.close()

    def test_swf(self):
        swf_file = open('swf/gacha160611_pet_android.swf', "rb")
        data = swf_file.read()
        swf_data = SwfData.get_swf(data)
        for tag in swf_data.tags:
            # if tag.code in [43]:
            print(tag)
