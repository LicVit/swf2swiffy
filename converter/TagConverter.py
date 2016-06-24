import swf_data.SwfData as SwfData
import swf_data.ShapeWithStyle as Shape
import converter.BasicDataTypeConverter as BasicConverter
import converter.ActionConverter as ActionConverter


class TagConverter:
    convert_control_tag = {
        1: lambda x: {'type': 2},
        12: lambda x: ActionConverter.convert(x),
        26: lambda x: convert_place_object2(x),
        28: lambda x: {'type': 4, 'depth': x.depth},
        43: lambda x: {'type': 15, 'label': x.name}
    }

    convert_tag = {
        2: lambda x: convert_shape(x),
        22: lambda x: convert_shape(x),
        32: lambda x: convert_shape(x),
        34: lambda x: convert_button(x),
        39: lambda x: convert_sprite(x),
    }

    def __init__(self, swf_tag):
        self.swf_tag = swf_tag  # type: SwfData.SwfTag

    def convert(self):
        code = self.swf_tag.code
        if code in self.convert_control_tag.keys():
            ret = self.convert_control_tag[code](self.swf_tag)
        elif code in self.convert_tag.keys():
            ret = self.convert_tag[code](self.swf_tag)
        else:
            raise Exception('unknown tag code %d' % code)
        return ret


def convert_place_object2(tag):
    ret = {'type': 3, 'depth': tag.depth}
    if tag.has_name:
        ret['name'] = tag.name
    if tag.has_character:
        ret['id'] = tag.character_id
    if tag.has_move:
        ret['replace'] = True
    if tag.has_matrix:
        matrix = tag.matrix
        ret['matrix'] = BasicConverter.matrix_to_string(matrix)
    return ret


def convert_sprite(tag):
    swiffy_tag = {'type': 7, 'id': tag.sprite_id, 'frameCount': tag.frame_count}
    control_tags = list()
    for control_tag in tag.control_tags:
        if control_tag.code == 0:
            break
        swiffy_control_tag = TagConverter(control_tag).convert()
        if swiffy_control_tag is None:
            break
        control_tags.append(swiffy_control_tag)
    if len(control_tags) > 0:
        swiffy_tag['tags'] = control_tags
    return swiffy_tag


def convert_shape(define_shape):
    ret = {'type': 1, 'id': define_shape.shape_id,
           'bounds': BasicConverter.rectangle_to_string(define_shape.shape_bounds),
           'flat': True}
    fill = define_shape.shapes.fill_styles.fill_styles
    line = define_shape.shapes.line_styles.line_styles
    swf_fill_styles = list()
    swf_line_styles = list()
    shapes = define_shape.shapes.shape_records
    paths = list()

    path = Path()
    for shape in shapes:
        if isinstance(shape, Shape.StyleChangeRecord):
            change_fill0 = shape.state_fill_style0 and shape.fill_style0 > 0
            change_fill1 = shape.state_fill_style1 and shape.fill_style1 > 0
            if change_fill0 or change_fill1:
                if not path.is_empty:
                    path.add_end()
                    paths.append(path.to_swiffy_object())
                    path = Path()

                if change_fill0:
                    current_fill0 = fill[shape.fill_style0 - 1]
                    if current_fill0 not in swf_fill_styles:
                        swf_fill_styles.append(current_fill0)
                    fill_index0 = swf_fill_styles.index(current_fill0)
                else:
                    fill_index0 = None

                if change_fill1:
                    current_fill1 = fill[shape.fill_style1 - 1]
                    if current_fill1 not in swf_fill_styles:
                        swf_fill_styles.append(current_fill1)
                    fill_index1 = swf_fill_styles.index(current_fill1)
                else:
                    fill_index1 = None

                path.set_fill(fill_index0, fill_index1)

            if shape.state_move_to and shape.move_delta_x != 0 and shape.move_delta_y != 0:
                path.add_move(shape.move_delta_x, shape.move_delta_y)

            if shape.state_line_style and shape.line_style > 0:
                current_line = line[shape.line_style - 1]
                if current_line not in swf_line_styles:
                    swf_line_styles.append(current_line)
                line_index = swf_line_styles.index(current_line)
                path.line = line_index

            if shape.state_new_styles:
                fill = shape.fill_styles.fill_styles
                line = shape.line_styles.line_styles

        elif isinstance(shape, Shape.StraightEdgeRecord):
            path.add_straight(shape.delta_x, shape.delta_y)
        elif isinstance(shape, Shape.CurvedEdgeRecord):
            path.add_curved(shape.control_delta_x, shape.control_delta_y, shape.anchor_delta_x, shape.anchor_delta_y)
        elif isinstance(shape, Shape.EndShapeRecord):
            path.add_end()
            paths.append(path.to_swiffy_object())

    ret['paths'] = paths
    if len(swf_fill_styles) > 0:
        ret['fillstyles'] = list()
        for style in swf_fill_styles:
            style_object = dict()
            if style.fill_style_type == 0x0:
                style_object['type'] = 1
                style_object['color'] = BasicConverter.rgb_to_int(style.color)
            elif style.fill_style_type == 0x10:
                style_object['type'] = 2
                style_object['transform'] = BasicConverter.matrix_to_string(style.gradient_matrix)
                style_object['gradient'] = [BasicConverter.gradient_to_dict(x) for x in style.gradient.gradient_records]
            else:
                raise NotImplementedError
            ret['fillstyles'].append(style_object)

    if len(swf_line_styles) > 0:
        ret['linestyle'] = list()
        for style in swf_line_styles:
            ret['linestyle'].append({'color': BasicConverter.rgb_to_int(style.color),
                                     'width': style.width
                                     })

    return ret


class Path:
    def __init__(self, path_string=str(), fill=0):
        self.path_string = path_string
        self.fill = fill
        self.pen_x = 0
        self.pen_y = 0
        self.is_empty = True
        self.line = 0

    def add_straight(self, delta_x, delta_y):
        self.pen_x += delta_x
        self.pen_y += delta_y
        straight_string = ''.join(BasicConverter.swiffy_integer(x) for x in [1, delta_x, delta_y])
        self.path_string += straight_string
        self.is_empty = False

    def add_curved(self, control_delta_x, control_delta_y, anchor_delta_x, anchor_delta_y):
        self.pen_x += anchor_delta_x + control_delta_x
        self.pen_y += anchor_delta_y + control_delta_y
        edge_string = ''.join(BasicConverter.swiffy_integer(x) for x in [2,
                                                                         control_delta_x,
                                                                         control_delta_y,
                                                                         anchor_delta_x + control_delta_x,
                                                                         anchor_delta_y + control_delta_y])
        self.path_string += edge_string
        self.is_empty = False

    def add_move(self, move_x, move_y):
        delta_x = move_x - self.pen_x
        delta_y = move_y - self.pen_y
        move_string = ''.join(BasicConverter.swiffy_integer(x) for x in [0, delta_x, delta_y])
        self.pen_x = move_x
        self.pen_y = move_y
        self.path_string += move_string

    def add_end(self):
        self.path_string += 'c'

    def set_fill(self, fill0, fill1):
        if fill0 is not None and fill0 > 0:
            self.fill = fill0
        elif fill1 is not None and fill1 > 0:
            self.fill = fill1

    def set_line(self, line):
        self.line = line

    def to_swiffy_object(self):
        return {
            'data': [self.path_string],
            'fill': self.fill
        }

    def __repr__(self):
        return 'Path(%r, %r' % (self.path_string, self.fill)


def convert_button(define_button):
    ret = {'type': 10}
    return ret