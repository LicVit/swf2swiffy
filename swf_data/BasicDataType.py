import struct

class RGB:
    def __init__(self, red, green, blue):
        self.red = red
        self.green = green
        self.blue = blue
        self.alpha = None

    def __repr__(self):
        return 'RGB(%r, %r, %r)' % (self.red, self.green, self.blue)


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


class Rectangle:
    def __init__(self, x_min=None, x_max=None, y_min=None, y_max=None):
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max

    def __repr__(self):
        return 'Rectangle(%r, %r, %r, %r)' % (self.x_min, self.x_max, self.y_min, self.y_max)


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
    return string, end
