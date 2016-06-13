import struct

import swf_data.BasicDataType as BasicData
import swf_data.BitReader as BitReader
from swf_data.ShapeWithStyle import ShapeWithStyle


class SwfData:
    def __init__(self, head=None, tags=list()):
        self.head = head
        self.tags = tags

    def read_data(self, data):
        self.head = SwfHead()
        offset = self.head.read_data(data)
        while offset < len(data):
            tag = SwfTag()
            offset = tag.read_data(data, offset)
            converted_tag = tag.analyze_tag()
            self.tags.append(converted_tag)
        return offset

    def __repr__(self):
        return 'SwfData(%r, %r)' % (self.head, self.tags)


def get_swf(data):
    ret = SwfData()
    ret.read_data(data)
    return ret


class SwfHead:
    def __init__(self, head_str=None, version=None, size=None, display_rect=None, frame_rate=None, frame_count=None):
        self.head_str = head_str
        self.version = version
        self.size = size
        self.display_rect = display_rect
        self.frame_count = frame_count
        self.frame_rate = frame_rate

    def read_data(self, data, offset=0):
        self.head_str = data[0:3]
        offset += 3
        self.version = struct.unpack_from('B', data, offset)[0]
        offset += 1
        self.size = struct.unpack_from('I', data, offset)[0]
        offset += 4
        reader = BitReader.memory_reader(data[offset:])
        self.display_rect = reader.read_rectangle()
        offset += reader.offset
        self.frame_rate = struct.unpack_from('H', data, offset)[0] / 256
        offset += 2
        self.frame_count = struct.unpack_from('H', data, offset)[0]
        offset += 2
        return offset

    def __repr__(self):
        return 'SwfHead(%r, %r, %r, %r, %r, %r)' % (
            self.head_str, self.version, self.size, self.display_rect, self.frame_rate, self.frame_count)


class SwfTag:
    def __init__(self, code=None, length=None, tag_data=None):
        self.code = code
        if length is None:
            if tag_data is not None:
                self.length = len(tag_data)
            else:
                self.length = None
        else:
            self.length = length
        self.tag_data = tag_data

    def read_data(self, data, offset=0):
        tag_byte = struct.unpack_from('H', data, offset)[0]
        offset += 2
        self.code = tag_byte >> 6
        _length = tag_byte & 63
        if _length == 63:
            _length = struct.unpack_from('I', data, offset)[0]
            offset += 4
        self.length = _length
        end = offset + self.length
        self.tag_data = data[offset:end]
        offset += self.length
        return offset

    def analyze_tag(self):
        if self.code == 0:
            return End()
        elif self.code == 1:
            return ShowFrame()
        elif self.code == 2:
            return DefineShape(tag_data=self.tag_data)
        elif self.code == 9:
            return SetBackgroundColor(tag_data=self.tag_data)
        elif self.code == 26:
            return PlaceObject2(tag_data=self.tag_data)
        elif self.code == 39:
            return DefineSprite(tag_data=self.tag_data)
        elif self.code == 69:
            return FileAttributes(tag_data=self.tag_data)
        elif self.code == 77:
            return MetaData(tag_data=self.tag_data)
        else:
            print(self.code)
            return self

    def __repr__(self):
        return 'SwfTag(%r, %r, %r)' % (self.code, self.length, self.tag_data)


class End(SwfTag):
    def __init__(self):
        super().__init__(code=0)

    def __repr__(self):
        return 'End()'


class ShowFrame(SwfTag):
    def __init__(self):
        super().__init__(code=1)

    def __repr__(self):
        return 'ShowFrame()'


class FileAttributes(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=69)
            self.use_direct_blit = kwargs.get('use_direct_blit')
            self.use_gpu = kwargs.get('use_gpu')
            self.has_metadata = kwargs.get('has_metadata')
            self.action_script3 = kwargs.get('action_script3')
            self.use_network = kwargs.get('use_network')
        else:
            super().__init__(code=69, tag_data=tag_data)
            reader = BitReader.memory_reader(tag_data)
            reader.read(1)  # Reserved
            self.use_direct_blit = reader.read(1)
            self.use_gpu = reader.read(1)
            self.has_metadata = reader.read(1)
            self.action_script3 = reader.read(1)
            reader.read(2)  # Reserved
            self.use_network = reader.read(1)

    def __repr__(self):
        return 'FileAttributes(use_direct_blit=%r, use_gpu=%r, has_metadata=%r, action_script3=%r, use_network=%r)' % (
            self.use_direct_blit, self.use_gpu, self.has_metadata, self.action_script3, self.use_network
        )


class MetaData(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=77)
            self.metadata = kwargs.get('metadata')
        else:
            super().__init__(code=77, tag_data=tag_data)
            self.metadata = tag_data.decode(encoding='utf-8')

    def __repr__(self):
        return 'MetaData(metadata=%r)' % self.metadata


class SetBackgroundColor(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=9)
            self.background_color = eval(kwargs.get('background_color'))
        else:
            super().__init__(code=9, tag_data=tag_data)
            self.background_color = BasicData.read_rgb(tag_data)

    def __repr__(self):
        return 'SetBackgroundColor(background_color=%r)' % self.background_color


class DefineShape(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=2)
            self.shape_id = kwargs.get('shape_id')
            self.shape_bounds = eval(kwargs.get('shape_bounds'))
            self.shapes = eval(kwargs.get('shapes'))
        else:
            super().__init__(code=2, tag_data=tag_data)
            self.shape_id = struct.unpack_from("H", tag_data)[0]
            offset = 2
            reader = BitReader.memory_reader(tag_data, offset)
            self.shape_bounds = reader.read_rectangle()
            offset += reader.offset
            self.shapes = ShapeWithStyle(shape_generation=1)
            self.shapes.read_data(tag_data[offset:])

    def __repr__(self):
        return 'DefineShape(shape_id=%r, shape_bounds=%r, shapes=%r)' % (self.shape_id, self.shape_bounds, self.shapes)


class DefineSprite(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=39)
            self.sprite_id = kwargs.get('sprite_id')
            self.frame_count = eval(kwargs.get('frame_count'))
            self.control_tags = eval(kwargs.get('control_tags'))
        else:
            super().__init__(code=39, tag_data=tag_data)
            self.sprite_id = struct.unpack_from("H", tag_data)[0]
            offset = 2
            self.frame_count = struct.unpack_from("H", tag_data, offset)[0]
            offset += 2
            if self.frame_count > 0:
                self.control_tags = list()
                while offset < len(tag_data):
                    tag = SwfTag()
                    offset = tag.read_data(tag_data, offset)
                    self.control_tags.append(tag.analyze_tag())

    def __repr__(self):
        return 'DefineSprite(sprite_id=%r, frame_count=%r, control_tags=%r)' % (
            self.sprite_id, self.frame_count, self.control_tags)


class PlaceObject2(SwfTag):
    def __init__(self, **kwargs):
        tag_data = kwargs.get('tag_data')
        if tag_data is None:
            super().__init__(code=26)
            self.depth = kwargs.get('depth')
            self.character_id = kwargs.get('character_id')
            self.matrix = eval(kwargs.get('matrix'))
            self.color_transform = kwargs.get('color_transform')
            self.ratio = kwargs.get('ratio')
            self.name = kwargs.get('name')
            self.clip_depth = kwargs.get('clip_depth')
            self.clip_actions = kwargs.get('clip_actions')
            self.has_clip_actions = int(self.clip_actions is not None)
            self.has_clip_depth = int(self.has_clip_depth is not None)
            self.has_name = int(self.has_name is not None)
            self.has_ratio = int(self.has_ratio is not None)
            self.has_color_transform = int(self.has_color_transform is not None)
            self.has_matrix = int(self.has_matrix is not None)
            self.has_character = int(self.has_character is not None)
            self.has_move = int(self.has_move is not None)
        else:
            super().__init__(code=26, tag_data=tag_data)
            reader = BitReader.memory_reader(tag_data)
            self.has_clip_actions = reader.read(1)
            self.has_clip_depth = reader.read(1)
            self.has_name = reader.read(1)
            self.has_ratio = reader.read(1)
            self.has_color_transform = reader.read(1)
            self.has_matrix = reader.read(1)
            self.has_character = reader.read(1)
            self.has_move = reader.read(1)
            offset = reader.offset
            self.depth = struct.unpack_from('H', tag_data, offset)[0]
            offset += 2
            reader.skip_bytes(2)
            if self.has_character:
                self.character_id = struct.unpack_from('H', tag_data, offset)[0]
                offset += 2
                reader.skip_bytes(2)
            if self.has_matrix:
                self.matrix = reader.read_matrix()
                offset = reader.offset
            if self.has_color_transform:
                raise NotImplementedError
            if self.has_ratio:
                self.ratio = struct.unpack_from('H', tag_data, offset)[0]
                offset += 2
                reader.skip_bytes(2)
            if self.has_name:
                self.name, string_end = BasicData.read_string(tag_data[offset:])
                offset += string_end
                reader.skip_bytes(string_end)
            if self.has_clip_depth:
                self.clip_depth = struct.unpack_from('H', tag_data, offset)
                offset += 2
                reader.skip_bytes(2)
            if self.has_clip_actions:
                raise NotImplementedError

    def __repr__(self):
        ret = 'PlaceObject2(depth=%r' % self.depth
        if self.has_character:
            ret += ', character_id=%r' % self.character_id
        if self.has_matrix:
            ret += ', matrix=%r' % self.matrix
        if self.has_color_transform:
            ret += ', color_transform=%r' % self.color_transform
        if self.has_ratio:
            ret += ', ratio=%r' % self.ratio
        if self.has_name:
            ret += ', name=%r' % self.name
        if self.has_clip_depth:
            ret += ', clip_depth=%r' % self.clip_depth
        if self.has_clip_actions:
            ret += ', has_clip_actions=%r' % self.has_clip_actions
        ret += ')'
        return ret
