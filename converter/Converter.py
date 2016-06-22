import json

import swf_data.SwfData as SwfData
import swf_data.BasicDataType as BasicData
import converter.BasicDataTypeConverter as BasicConverter
import converter.TagConverter as TagConverter


class Converter:
    def __init__(self, data):
        self.swf_data = SwfData.get_swf(data)
        self.swiffy_data = dict()
        self.json_string = None

    def to_swiffy(self, intent=2):
        if self.json_string is None:
            self._convert_head()
            self._convert_tags()
            self.json_string = json.dumps(self.swiffy_data, indent=intent)
        return self.json_string

    def to_html(self):
        head = '<!doctype html>\
<html>\
  <head>\
    <meta charset="utf-8">\
    <meta http-equiv="X-UA-Compatible" content="IE=edge">\
    <title>Swiffy Output</title>\
    <script type="text/javascript" src="http://localhost/snap/dist/runtime-8.0-format.js"></script>\
    <script> swiffyobject = '
        foot = ';\
    </script>\
    <style>html, body {width: 100%; height: 100%}</style>\
  </head>\
  <body style="margin: 0; overflow: hidden">\
    <div id="swiffycontainer" style="width: 240px; height: 300px">\
    </div>\
    <script>\
      var stage = new swiffy.Stage(document.getElementById(\'swiffycontainer\'),\
          swiffyobject, {});\
      stage.start();\
    </script>\
  </body>\
</html>'
        return head + self.to_swiffy() + foot

    attribute_tag = {
        9: lambda x: {'backgroundColor': BasicConverter.rgb_to_int(x.background_color)},
        69: lambda x: {'as3': bool(x.action_script3)},
        77: lambda x: dict()

    }

    def _convert_tags(self):
        for tag in self.swf_data.tags:  # type: SwfData.SwfTag
            if isinstance(tag, SwfData.End):
                break
            elif tag.code in self.attribute_tag:
                swiffy_attribute = self.attribute_tag[tag.code](tag)
                self.swiffy_data.update(swiffy_attribute)
            else:
                swiffy_tag = TagConverter.TagConverter(tag).convert()
                if len(swiffy_tag) > 0:
                    if 'tags' not in self.swiffy_data.keys():
                        self.swiffy_data['tags'] = list()
                    self.swiffy_data['tags'].append(swiffy_tag)

    def _convert_head(self):
        head = self.swf_data.head  # type: SwfData.SwfHead
        self.swiffy_data['frameRate'] = head.frame_rate
        self.swiffy_data['frameCount'] = head.frame_count
        frame_size = head.display_rect  # type: BasicData.Rectangle
        self.swiffy_data['frameSize'] = {
            'xmin': frame_size.x_min,
            'xmax': frame_size.x_max,
            'ymin': frame_size.y_min,
            'ymax': frame_size.y_max
        }
        self.swiffy_data['fileSize'] = head.size
        self.swiffy_data['version'] = head.version
        self.swiffy_data['v'] = '8.0.0'



