class Buffer:
    def __init__(self):
        self.buffer = None
        self.file = None
        self._offset = None

    def skip_bytes(self, size):
        raise NotImplementedError

    def next_byte(self):
        raise NotImplementedError

    def offset(self):
        raise NotImplementedError


class MemoryBuffer(Buffer):
    def __init__(self, buffer):
        super().__init__()
        self.buffer = buffer
        self._offset = 0

    def skip_bytes(self, size):
        self._offset += size

    def next_byte(self):
        if self.offset < len(self.buffer):
            ret = self.buffer[self.offset]
            self._offset += 1
        else:
            ret = None
        return ret

    @property
    def offset(self):
        return self._offset


class FileBuffer(Buffer):
    def __init__(self, file):
        super().__init__()
        self.file = file

    def skip_bytes(self, size):
        raise Exception('cannot move file point')

    def next_byte(self):
        ret = self.file.read(1)
        if ret is not None:
            return ret[0]
        else:
            return None

    @property
    def offset(self):
        return self.file.tell()


class BitReader:
    def __init__(self, source: Buffer):
        self.source = source
        self.pool = 0
        self.pool_length = 0

    def read(self, count):
        if count == 0:
            return 0
        while self.pool_length < count:
            self.pool <<= 8
            self.pool += self.source.next_byte()
            self.pool_length += 8

        bit_diff = self.pool_length - count
        ret = self.pool >> bit_diff
        self.pool &= ((1 << bit_diff) - 1)
        self.pool_length = bit_diff

        return ret

    def read_signed(self, count):
        if count == 0:
            return 0
        ret = self.read(count)
        if ret > (1 << (count - 1)):
            ret -= (1 << count)
        return ret

    def skip_bytes(self, size):
        self.source.skip_bytes(size)
        self.pool = 0
        self.pool_length = 0

    @property
    def offset(self):
        return self.source.offset

    @property
    def remain_buffer(self):
        if self.source.offset is not None and self.source.buffer is not None:
            return self.source.buffer[self.source.offset:]
        else:
            return None

    def read_rectangle(self):
        bits = self.read(5)
        x_min = self.read_signed(bits)
        x_max = self.read_signed(bits)
        y_min = self.read_signed(bits)
        y_max = self.read_signed(bits)
        from swf_data.BasicDataType import Rectangle
        ret = Rectangle(x_min, x_max, y_min, y_max)
        return ret

    def read_matrix(self):
        has_scale = self.read(1)
        if has_scale:
            scale_bits = self.read(5)
            scale_x = self.read_signed(scale_bits) / 65536
            scale_y = self.read_signed(scale_bits) / 65536
        else:
            scale_x = None
            scale_y = None
        has_rotate = self.read(1)
        if has_rotate:
            rotate_bits = self.read(5)
            rotate_skew0 = self.read_signed(rotate_bits) / 65536
            rotate_skew1 = self.read_signed(rotate_bits) / 65536
        else:
            rotate_skew0 = None
            rotate_skew1 = None
        translate_bits = self.read(5)
        translate_x = self.read_signed(translate_bits)
        translate_y = self.read_signed(translate_bits)
        from swf_data.BasicDataType import Matrix
        ret = Matrix(scale_x, scale_y, rotate_skew0, rotate_skew1, translate_x, translate_y)
        return ret


def memory_reader(memory_data, offset=0):
    return BitReader(MemoryBuffer(memory_data[offset:]))
