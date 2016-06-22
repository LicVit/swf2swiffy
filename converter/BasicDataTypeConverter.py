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