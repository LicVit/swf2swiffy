import json

import swf_data.SwfData as SwfData
import swf_data.BasicDataType as BasicData
import swf_data.ShapeWithStyle as Shape


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

    def _convert_tags(self):
        for tag in self.swf_data.tags:  # type: SwfData.SwfTag
            swiffy_tag = dict()
            if isinstance(tag, SwfData.End):
                break
            elif isinstance(tag, SwfData.ShowFrame):
                swiffy_tag = self._convert_control_tags(tag)
            elif isinstance(tag, SwfData.DefineShape):
                swiffy_tag = {'type': 1, 'id': tag.shape_id, 'bounds': rectangle_to_string(tag.shape_bounds),
                              'flat': True}
                swiffy_tag.update(self._convert_shape(tag))
            elif isinstance(tag, SwfData.SetBackgroundColor):
                self.swiffy_data['backgroundColor'] = rgb_to_int(tag.background_color)
            elif isinstance(tag, SwfData.PlaceObject2):
                swiffy_tag = self._convert_control_tags(tag)
            elif isinstance(tag, SwfData.DefineSprite):
                swiffy_tag = {'type': 7, 'id': tag.sprite_id, 'frameCount': tag.frame_count}
                control_tags = list()
                for control_tag in tag.control_tags:
                    swiffy_control_tag = self._convert_control_tags(control_tag)
                    if swiffy_control_tag is None:
                        break
                    control_tags.append(swiffy_control_tag)
                if len(control_tags) > 0:
                    swiffy_tag['tags'] = control_tags
            elif isinstance(tag, SwfData.FileAttributes):
                self.swiffy_data['as3'] = bool(tag.action_script3)
            elif tag.code == 77:
                pass
            else:
                raise Exception('unknown tag code %d' % tag.code)
            if len(swiffy_tag) > 0:
                if 'tags' not in self.swiffy_data.keys():
                    self.swiffy_data['tags'] = list()
                self.swiffy_data['tags'].append(swiffy_tag)

    def _convert_control_tags(self, tag):
        if isinstance(tag, SwfData.ShowFrame):
            return {'type': 2}
        elif isinstance(tag, SwfData.PlaceObject2):
            ret = {'type': 3, 'depth': tag.depth}
            if tag.has_name:
                ret['name'] = tag.name
            if tag.has_character:
                ret['id'] = tag.character_id
            if tag.has_move:
                ret['replace'] = True
            if tag.has_matrix:
                matrix = tag.matrix
                ret['matrix'] = matrix_to_string(matrix)
            return ret
        elif isinstance(tag, SwfData.End):
            return None
        else:
            raise NotImplementedError

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

    def _convert_shape(self, define_shape):
        ret = dict()
        fill = define_shape.shapes.fill_styles.fill_styles
        line = define_shape.shapes.line_styles.line_styles
        swf_fill_styles = list()
        swf_line_styles = list()
        shapes = define_shape.shapes.shape_records
        paths = list()
        path = dict()
        path_string = str()
        path['data'] = list()
        for shape in shapes:
            if isinstance(shape, Shape.StyleChangeRecord):
                if len(path_string) > 0:  # add path
                    path_string += 'c'
                    path['data'] = list()
                    path['data'].append(path_string)
                    paths.append(path)
                    path = dict()
                    path_string = str()

                if shape.state_move_to and shape.move_delta_x != 0 and shape.move_delta_y != 0:
                    move_string = ''.join(swiffy_integer(x) for x in [0, shape.move_delta_x, shape.move_delta_y])
                    path_string += move_string
                if shape.state_fill_style0 and shape.fill_style0 > 0:
                    current_fill0 = fill[shape.fill_style0 - 1]
                    if current_fill0 not in swf_fill_styles:
                        swf_fill_styles.append(current_fill0)
                    fill_index0 = swf_fill_styles.index(current_fill0)
                    path['fill'] = fill_index0

                if shape.state_fill_style1 and shape.fill_style1 > 0:
                    current_fill1 = fill[shape.fill_style1 - 1]
                    if current_fill1 not in swf_fill_styles:
                        swf_fill_styles.append(current_fill1)
                    fill_index1 = swf_fill_styles.index(current_fill1)
                    path['fill'] = fill_index1

                if shape.state_line_style and shape.line_style > 0:
                    current_line = line[shape.line_style - 1]
                    if current_line not in swf_line_styles:
                        swf_line_styles.append(current_line)
                    line_index = swf_fill_styles.index(current_line)
                    raise NotImplementedError

                if shape.state_new_styles:
                    fill = shape.fill_styles.fill_styles
                    line = shape.line_styles.line_styles

            elif isinstance(shape, Shape.StraightEdgeRecord):
                straight_string = ''.join(swiffy_integer(x) for x in [1, shape.delta_x, shape.delta_y])
                path_string += straight_string

            elif isinstance(shape, Shape.CurvedEdgeRecord):
                edge_string = ''.join(swiffy_integer(x) for x in [2,
                                                                  shape.control_delta_x,
                                                                  shape.control_delta_y,
                                                                  shape.anchor_delta_x + shape.control_delta_x,
                                                                  shape.anchor_delta_y + shape.control_delta_y])
                path_string += edge_string
            elif isinstance(shape, Shape.EndShapeRecord):
                if len(path_string) > 0:
                    path_string += 'c'
                    path['data'] = list()
                    path['data'].append(path_string)
                    paths.append(path)
                break
            else:
                raise Exception

        ret['paths'] = paths
        if len(swf_fill_styles) > 0:
            ret['fillstyles'] = list()
            for style in swf_fill_styles:
                style_object = dict()
                style_object['color'] = rgb_to_int(style.color)
                if style.fill_style_type == 0x0:
                    style_object['type'] = 1
                else:
                    raise NotImplementedError
                ret['fillstyles'].append(style_object)

        return ret


def rectangle_to_string(rectangle):
    rectangle_string = ''.join(swiffy_integer(x) for x in [
        rectangle.x_min,
        rectangle.y_min,
        rectangle.x_max - rectangle.x_min,
        rectangle.y_max - rectangle.y_min,
    ])
    return rectangle_string


def matrix_to_string(matrix):
    if not matrix.has_rotate and not matrix.has_scale and matrix.translate_y == 0 and matrix.translate_x == 0:
        return 0
    matrix_string = str()
    if matrix.has_scale:
        matrix_string += swiffy_integer(round((matrix.scale_x - 1) * 65536))
    else:
        matrix_string += ':'
    if matrix.has_rotate:
        matrix_string += ''.join(swiffy_integer(round(x * 65536)) for x in [matrix.rotate_skew0, matrix.rotate_skew1])
    else:
        matrix_string += '::'
    if matrix.has_scale:
        matrix_string += swiffy_integer(round((matrix.scale_y - 1) * 65536))
    else:
        matrix_string += ':'
    matrix_string += swiffy_integer(matrix.translate_x)
    matrix_string += swiffy_integer(matrix.translate_y)
    return matrix_string


def rgb_to_int(color):
    red = color.red
    green = color.green
    blue = color.blue
    integer = blue + (green << 8) + (red << 16)
    # if (integer & (1 << 23)) > 0:
    integer += (-1 << 24)
    return integer


def swiffy_integer(integer):
    if integer is None or integer == 0:
        return ':'
    elif 0 < integer <= 26:
        return chr(integer + 96)
    elif 0 > integer >= -26:
        return chr(-integer + 64)
    elif integer > 26:
        remain = integer // 10
        end = str(integer % 10)
        while remain > 26:
            end = str(remain % 10) + end
            remain //= 10
        return str(end) + swiffy_integer(remain)
    else:
        end = str((-integer) % 10)
        remain = -((-integer) // 10)
        while remain < -26:
            end = str((-remain) % 10) + end
            remain = -((-remain) // 10)
        return str(end) + swiffy_integer(remain)
