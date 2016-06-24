import struct
import swf_data.BasicDataType as BasicData
import swf_data.BitReader as BitReader


class ShapeWithStyle:
    def __init__(self, **kwargs):
        self.shape_generation = kwargs.get('shape_generation')
        self.fill_styles = eval(kwargs.get('fill_styles', 'None'))
        self.line_styles = eval(kwargs.get('line_styles', 'None'))
        self.num_fill_bits = kwargs.get('num_fill_bits')
        self.num_line_bits = kwargs.get('num_fill_bits')
        self.shape_records = eval(kwargs.get('shape_records', 'None'))

    def read_data(self, data):
        self.fill_styles = FillStyleArray(shape_generation=self.shape_generation)
        offset = self.fill_styles.read_data(data)
        self.line_styles = LineStyleArray(shape_generation=self.shape_generation)
        size = self.line_styles.read_data(data[offset:])
        offset += size

        reader = BitReader.memory_reader(data, offset)
        self.num_fill_bits = reader.read(4)
        self.num_line_bits = reader.read(4)
        offset += reader.offset

        self.shape_records = list()
        reader = BitReader.memory_reader(data[offset:])
        while True:
            record, reader = self.read_record_data(reader)
            self.shape_records.append(record)
            if isinstance(record, EndShapeRecord):
                break
        offset += reader.offset
        return offset

    def read_record_data(self, bit_reader):
        type_flag = bit_reader.read(1)
        if type_flag == 0:
            end_flag = bit_reader.read(5)
            if end_flag == 0:
                record = EndShapeRecord()
            else:
                record = StyleChangeRecord(num_fill_bits=self.num_fill_bits, num_line_bits=self.num_line_bits,
                                           end_flag=end_flag, shape_generation=self.shape_generation)
        else:
            straight_flag = bit_reader.read(1)
            if straight_flag:
                record = StraightEdgeRecord()
            else:
                record = CurvedEdgeRecord()
        bit_reader = record.read_data(bit_reader)
        if isinstance(record, StyleChangeRecord) and record.state_new_styles:
            self.num_fill_bits, self.num_line_bits = record.get_new_bits()
        return record, bit_reader

    def __repr__(self):
        return 'ShapeWithStyle(fill_styles=%r, line_styles=%r, num_fill_bits=%r, ' \
               'num_line_bits=%r, shape_records=%r)' % (
                   self.fill_styles, self.line_styles, self.num_fill_bits,
                   self.num_line_bits, self.shape_records)

    def __str__(self):
        ret = 'ShapeWithStyle:\n' \
               '  fill_styles=%s,\n' \
               '  line_styles=%s,\n' \
               '  num_fill_bits=%s,\n' \
               '  num_line_bits=%s,\n' \
               '  shape_records=\n' % (
                   self.fill_styles, self.line_styles, self.num_fill_bits,
                   self.num_line_bits, )
        for record in self.shape_records:
            ret += '\t%s\n' % record

        return ret


class ShapeRecord:
    def __init__(self, type_flag):
        self.type_flag = type_flag

    def read_data(self, data):
        raise NotImplementedError


class FillStyleArray:
    def __init__(self, fill_style_count=None, fill_style_count_extended=None, fill_styles=None, **kwargs):
        self.shape_generation = kwargs.get('shape_generation')
        self.fill_style_count = fill_style_count
        self.fill_style_count_extended = fill_style_count_extended
        self.fill_styles = fill_styles

    def read_data(self, data):
        self.fill_style_count = struct.unpack_from('B', data)[0]
        offset = 1
        if self.fill_style_count == 0xFF:
            self.fill_style_count_extended = struct.unpack_from('H', data, offset)[0]
            offset += 2
            count = self.fill_style_count_extended
        else:
            self.fill_style_count_extended = None
            count = self.fill_style_count
        self.fill_styles = list()
        for i in range(0, count):
            style = FillStyle(shape_generation=self.shape_generation)
            size = style.read_data(data[offset:])
            self.fill_styles.append(style)
            offset += size
        return offset

    def __repr__(self):
        ret = 'FillStyleArray(%r, %r, %r)' % (self.fill_style_count, self.fill_style_count_extended, self.fill_styles)
        return ret


class FillStyle:
    def __init__(self, fill_style_type=None, color=None, gradient_matrix=None, gradient=None, **kwargs):
        self.shape_generation = kwargs.get('shape_generation')
        self.fill_style_type = fill_style_type
        self.color = color
        self.gradient_matrix = gradient_matrix
        self.gradient = gradient

    def read_data(self, data):
        self.fill_style_type = struct.unpack_from('B', data)[0]
        offset = 1
        if self.fill_style_type == 0x00:
            if self.shape_generation <= 2:
                self.color = BasicData.read_rgb(data[offset:])
                offset += 3
            else:
                self.color = BasicData.read_rgba(data[offset:])
                offset += 4
        if self.fill_style_type in [0x10, 0x12, 0x13]:
            reader = BitReader.memory_reader(data, offset)
            self.gradient_matrix = reader.read_matrix()
            offset += reader.offset
        if self.fill_style_type in [0x10, 0x12]:
            self.gradient, size = BasicData.read_gradient(data[offset:], self.shape_generation)
            offset += size
        return offset

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __repr__(self):
        return 'FillStyle(%r, %r, %r, %r)' % (self.fill_style_type, self.color, self.gradient_matrix, self.gradient)


class LineStyleArray:
    def __init__(self, line_style_count=None, line_style_count_extended=None, line_styles=None, **kwargs):
        self.shape_generation = kwargs.get('shape_generation')
        self.line_style_count = line_style_count
        self.line_style_count_extended = line_style_count_extended
        self.line_styles = line_styles

    def read_data(self, data):
        self.line_style_count = struct.unpack_from('B', data)[0]
        offset = 1
        if self.line_style_count == 0xFF:
            self.line_style_count_extended = struct.unpack_from('H', data, offset)[0]
            offset += 2
            count = self.line_style_count_extended
        else:
            self.line_style_count_extended = None
            count = self.line_style_count

        self.line_styles = list()
        for i in range(0, count):
            style = LineStyle(shape_generation=self.shape_generation)
            size = style.read_data(data[offset:])
            self.line_styles.append(style)
            offset += size
        return offset

    def __repr__(self):
        ret = 'LineStyleArray(%r, %r, %r)' % (self.line_style_count, self.line_style_count_extended, self.line_styles)
        return ret


class LineStyle:
    def __init__(self, width=None, color=None, **kwargs):
        self.shape_generation = kwargs.get('shape_generation')
        self.width = width
        self.color = color

    def read_data(self, data):
        self.width = struct.unpack_from('H', data)[0]
        offset = 2
        if self.shape_generation <= 2:
            self.color = BasicData.read_rgb(data[offset:])
            offset += 3
        else:
            self.color = BasicData.read_rgba(data[offset:])
            offset += 4
        return offset

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __repr__(self):
        ret = 'LineStyle(%r, %r)' % (self.width, self.color)
        return ret


class StyleChangeRecord(ShapeRecord):
    def __init__(self, num_fill_bits, num_line_bits, end_flag, **kwargs):
        super().__init__(type_flag=0)
        self.move_delta_x = kwargs.get('move_delta_x')
        self.move_delta_y = kwargs.get('move_delta_y')
        self.fill_style0 = kwargs.get('fill_style0')
        self.fill_style1 = kwargs.get('fill_style1')
        self.line_style = kwargs.get('line_style')
        self.fill_styles = eval(kwargs.get('fill_styles', 'None'))
        self.line_styles = eval(kwargs.get('line_styles', 'None'))
        self.num_fill_bits = num_fill_bits
        self.num_line_bits = num_line_bits
        self.shape_generation = kwargs.get('shape_generation')
        self.state_new_styles = end_flag & 0x10 > 0
        self.state_line_style = end_flag & 0x8 > 0
        self.state_fill_style1 = end_flag & 0x4 > 0
        self.state_fill_style0 = end_flag & 0x2 > 0
        self.state_move_to = end_flag & 0x1 > 0
        self.new_fill_bits = None
        self.new_line_bits = None

    def read_data(self, bit_reader):
        if self.state_move_to:
            move_bits = bit_reader.read(5)
            self.move_delta_x = bit_reader.read_signed(move_bits)
            self.move_delta_y = bit_reader.read_signed(move_bits)
        if self.state_fill_style0:
            self.fill_style0 = bit_reader.read(self.num_fill_bits)
        if self.state_fill_style1:
            self.fill_style1 = bit_reader.read(self.num_fill_bits)
        if self.state_line_style:
            self.line_style = bit_reader.read(self.num_line_bits)
        data = bit_reader.remain_buffer
        offset = 0
        if self.state_new_styles:
            self.fill_styles = FillStyleArray(shape_generation=self.shape_generation)
            size = self.fill_styles.read_data(data[offset:])
            offset += size
            self.line_styles = LineStyleArray(shape_generation=self.shape_generation)
            size = self.line_styles.read_data(data[offset:])
            offset += size
            num_bits = struct.unpack_from("B", data, offset)[0]
            offset += 1
            self.new_fill_bits = num_bits >> 4
            self.new_line_bits = num_bits & 0xF
            bit_reader = BitReader.memory_reader(data[offset:])
        return bit_reader

    def get_new_bits(self):
        return self.new_fill_bits, self.new_line_bits

    def __repr__(self):
        ret = 'StyleChangeRecord('
        ret += 'num_fill_bits=%r, num_line_bits=%r' % (self.num_fill_bits, self.num_line_bits)
        if self.state_move_to:
            ret += ', move_delta_x=%r' % self.move_delta_x
            ret += ', move_delta_y=%r' % self.move_delta_y
        if self.state_fill_style0:
            ret += ', fill_style0=%r' % self.fill_style0
        if self.state_fill_style1:
            ret += ', fill_style1=%r' % self.fill_style1
        if self.state_line_style:
            ret += ', line_style=%r' % self.line_style
        if self.state_new_styles:
            ret += ', fill_styles=%r, line_styles=%r, new_fill_bits=%r, new_line_bits=%r' % (
                self.fill_styles, self.line_styles, self.new_fill_bits, self.new_line_bits)
        return ret


class CurvedEdgeRecord(ShapeRecord):
    def __init__(self, control_delta_x=0, control_delta_y=0, anchor_delta_x=0, anchor_delta_y=0, **kwargs):
        super().__init__(type_flag=1)
        self.straight_flag = 0
        self.num_bits = kwargs.get('num_bits')
        self.control_delta_x = control_delta_x
        self.control_delta_y = control_delta_y
        self.anchor_delta_x = anchor_delta_x
        self.anchor_delta_y = anchor_delta_y
        self.is_end = False

    def read_data(self, bit_reader):
        self.num_bits = bit_reader.read(4)
        self.control_delta_x = bit_reader.read_signed(self.num_bits + 2)
        self.control_delta_y = bit_reader.read_signed(self.num_bits + 2)
        self.anchor_delta_x = bit_reader.read_signed(self.num_bits + 2)
        self.anchor_delta_y = bit_reader.read_signed(self.num_bits + 2)
        return bit_reader

    def __repr__(self):
        ret = 'CurvedEdgeRecord(%r, %r, %r, %r)' % (
            self.control_delta_x, self.control_delta_y, self.anchor_delta_x, self.anchor_delta_y
        )
        return ret


class StraightEdgeRecord(ShapeRecord):
    def __init__(self, delta_x=0, delta_y=0, **kwargs):
        super().__init__(type_flag=1)
        self.straight_flag = 1
        self.num_bits = kwargs.get('num_bits')
        self.general_line_flag = kwargs.get('general_line_flag')
        self.vert_line_flag = kwargs.get('vert_line_flag')
        self.delta_x = delta_x
        self.delta_y = delta_y
        self.is_end = False

    def read_data(self, bit_reader):
        self.num_bits = bit_reader.read(4)
        self.general_line_flag = bit_reader.read(1)
        if self.general_line_flag == 0:
            self.vert_line_flag = bit_reader.read(1)
        if self.general_line_flag or self.vert_line_flag == 0:
            self.delta_x = bit_reader.read_signed(self.num_bits + 2)
        if self.general_line_flag or self.vert_line_flag == 1:
            self.delta_y = bit_reader.read_signed(self.num_bits + 2)
        return bit_reader

    def __repr__(self):
        ret = 'StraightEdgeRecord(%r, %r)' % (
            self.delta_x, self.delta_y
        )
        return ret


class EndShapeRecord(ShapeRecord):
    def __init__(self):
        super().__init__(type_flag=0)

    def read_data(self, bit_reader):
        return bit_reader

    def __repr__(self):
        ret = 'EndShapeRecord()'
        return ret
