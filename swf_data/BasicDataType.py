import struct
import swf_data.BitReader as BitReader


class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = None

    def __repr__(self):
        return 'RGB(%r, %r, %r)' % (self.red, self.green, self.blue)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__


class RGBA(RGB):
    def __init__(self, red, green, blue, alpha):
        super().__init__(red, green, blue)
        self.alpha = alpha

    def __repr__(self):
        return 'RGBA(%r, %r, %r, %r)' % (self.red, self.green, self.blue, self.alpha)


class Matrix:
    def __init__(self, scale_x=None, scale_y=None, rotate_skew0=None, rotate_skew1=None, translate_x=None,
                 translate_y=None):
        self.has_scale = int(scale_x is not None or scale_y is not None)
        self.scale_x = scale_x
        self.scale_y = scale_y
        self.has_rotate = int(rotate_skew0 is not None or rotate_skew1 is not None)
        self.rotate_skew0 = rotate_skew0
        self.rotate_skew1 = rotate_skew1
        self.translate_x = translate_x
        self.translate_y = translate_y

    def to_matrix_tuple(self, twink):
        ret = (
            self.scale_x,
            self.rotate_skew0,
            self.rotate_skew1,
            self.scale_y,
            self.translate_x / twink,
            self.translate_y / twink
        )
        return ret

    def __repr__(self):
        ret = 'Matrix('
        if self.has_scale:
            ret += 'scale_x=%r, scale_y=%r, ' % (self.scale_x, self.scale_y)
        if self.has_rotate:
            ret += 'rotate_skew0=%r, rotate_skew1=%r, ' % (self.rotate_skew0, self.rotate_skew1)
        ret += 'translate_x=%r, translate_y=%r)' % (self.translate_x, self.translate_y)
        return ret

    def __str__(self):
        ret = 'Trans({0},{1})'.format(self.translate_x, self.translate_y)
        if self.has_scale:
            ret += ', Scale({0:.2f},{1:.2f})'.format(self.scale_x, self.scale_y)
        if self.has_rotate:
            ret += ', Rotate({0:.2f},{1:.2f})'.format(self.rotate_skew0, self.rotate_skew1)
        return ret


class Gradient:
    def __init__(self, spread_mode=None, interpolation_mode=None, num_gradients=None, gradient_records=None,
                 shape_generation=1):
        self.spread_mode = spread_mode
        self.interpolation_mode = interpolation_mode
        self.num_gradients = num_gradients
        self.gradient_records = gradient_records
        self.shape_generation = shape_generation

    def __repr__(self):
        ret = 'Gradient(%r, %r, %r, %r, shape_generation=%r)' % (
            self.spread_mode,
            self.interpolation_mode,
            self.num_gradients,
            self.gradient_records,
            self.shape_generation)
        return ret


class GradientRecord:
    def __init__(self, ratio=None, color=None, shape_generation=1):
        self.ratio = ratio
        self.color = color
        self.shape_generation = shape_generation

    def __repr__(self):
        ret = 'GradientRecord(%r, %r, shape_generation=%r)' % (
            self.ratio,
            self.color,
            self.shape_generation)
        return ret


class Rectangle:
    def __init__(self, x_min=None, x_max=None, y_min=None, y_max=None):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def __repr__(self):
        return 'Rectangle(%r, %r, %r, %r)' % (self.x_min, self.x_max, self.y_min, self.y_max)


class CXFormAlpha:
    def __init__(self, red_mult_term=0, green_mult_term=0, blue_mult_term=0, alpha_mult_term=0,
                 red_add_term=0, green_add_term=0, blue_add_term=0, alpha_add_term=0):
        self.red_mult_term = red_mult_term
        self.green_mult_term = green_mult_term
        self.blue_mult_term = blue_mult_term
        self.red_add_term = red_add_term
        self.green_add_term = green_add_term
        self.blue_add_term = blue_add_term
        self.alpha_mult_term = alpha_mult_term
        self.alpha_add_term = alpha_add_term

    def __repr__(self):
        ret = 'CXForm(%r, %r, %r, %r, %r, %r, %r, %r)' % (
            self.red_mult_term, self.green_mult_term, self.blue_mult_term, self.alpha_mult_term,
            self.red_add_term, self.green_add_term, self.blue_add_term, self.alpha_add_term)
        return ret


class ButtonRecord:
    def __init__(self, state_hit_test=None, state_down=None, state_over=None,
                 state_up=None, character_id=None, place_depth=None, place_matrix=None, color_transform=None,
                 filter_list=None, blend_mode=None):
        self.has_blend_mode = blend_mode is not None
        self.has_filter_list = filter_list is not None
        self.state_hit_test = state_hit_test
        self.state_down = state_down
        self.state_up = state_up
        self.state_over = state_over
        self.chatacter_id = character_id
        self.place_depth = place_depth
        self.place_matrix = place_matrix
        self.color_transform = color_transform
        self.filter_list = filter_list
        self.blend_mode = blend_mode

    def __repr__(self):
        ret = 'ButtonRecord(%r, %r, %r, %r, %r, %r, %r, %r, %r, %r)' % \
              (self.state_hit_test, self.state_down, self.state_over, self.state_up, self.chatacter_id,
               self.place_depth, self.place_matrix, self.color_transform, self.filter_list, self.blend_mode)
        return ret


def read_rgb(data):
    ret = RGB(*(struct.unpack_from('BBB', data)))
    return ret


def read_rgba(data):
    ret = RGBA(*(struct.unpack_from('BBBB', data)))
    return ret


def read_string(data):
    end = 0
    while int(data[end]) > 0:
        end += 1
    string = data[:end].decode(encoding='shift-jis')
    return string, end + 1


def read_gradient(data, shape_generation=1):
    ret = Gradient(shape_generation=shape_generation)
    first_byte = struct.unpack_from('B', data)[0]
    offset = 1
    ret.spread_mode = first_byte >> 6
    ret.interpolation_mode = (first_byte >> 4) & 3
    ret.num_gradients = first_byte % 0xF
    gradient_records = list()
    for i in range(0, ret.num_gradients):
        gradient_record, size = read_gradient_record(data[offset:], shape_generation=shape_generation)
        gradient_records.append(gradient_record)
        offset += size
    ret.gradient_records = gradient_records
    return ret, offset


def read_gradient_record(data, shape_generation=1):
    ret = GradientRecord(shape_generation=shape_generation)
    ret.ratio = struct.unpack_from('B', data, 0)[0]
    offset = 1
    if shape_generation <= 2:
        ret.color = read_rgb(data[offset:])
        offset += 3
    else:
        ret.color = read_rgba(data[offset:])
        offset += 4

    return ret, offset


def read_button_record(data, button_generation=1):
    ret = ButtonRecord()
    flag_byte = struct.unpack_from('B', data)[0]
    offset = 1
    ret.has_blend_mode = (flag_byte & 0x20) > 0
    ret.has_filter_list = (flag_byte & 0x10) > 0
    ret.state_hit_test = (flag_byte & 0x8) > 00
    ret.state_down = (flag_byte & 0x4) > 00
    ret.state_over = (flag_byte & 0x2) > 00
    ret.state_up = (flag_byte & 0x1) > 0
    ret.chatacter_id = struct.unpack_from('H', data, offset)[0]
    offset += 2
    ret.place_depth = struct.unpack_from('H', data, offset)[0]
    offset += 2
    bit_reader = BitReader.memory_reader(data[offset:])
    ret.place_matrix = bit_reader.read_matrix()
    if button_generation>=2:
        ret.color_transform = bit_reader.read_cx_form_alpha()
        offset += bit_reader.offset
        if ret.has_filter_list:
            raise NotImplementedError
        if ret.has_blend_mode:
            ret.blend_mode = struct.unpack_from('B', data, offset)[0]
            offset += 1
    return ret, offset
