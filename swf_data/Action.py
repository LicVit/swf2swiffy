import struct
import swf_data.BasicDataType as BasicData


class Action:
    def __init__(self, code=None, length=None, action_data=None):
        self.code = code
        self.length = length
        self.action_data = action_data

    def read_data(self, data, offset=0):
        self.code = struct.unpack_from('B', data, offset)[0]
        offset += 1
        if self.code > 0x80:
            self.length = struct.unpack_from('H', data, offset)[0]
            offset += 2
            self.action_data = data[offset:(offset + self.length)]
            offset += self.length
        else:
            self.length = 0
            self.action_data = None
        return offset

    def analyze_action(self):
        if self.code == 0:
            return ActionEnd()
        elif self.code == 0x6:
            return ActionPlay()
        elif self.code == 0x7:
            return ActionStop()
        elif self.code == 0xE:
            return ActionEquals()
        elif self.code == 0xF:
            return ActionLess()
        elif self.code == 0xA:
            return ActionAdd()
        elif self.code == 0x12:
            return ActionNot()
        elif self.code == 0x17:
            return ActionPop()
        elif self.code == 0x1C:
            return ActionGetVariable()
        elif self.code == 0x1D:
            return ActionSetVariable()
        elif self.code == 0x2B:
            return ActionCastOp()
        elif self.code == 0x3D:
            return ActionCallFunction()
        elif self.code == 0x81:
            return ActionGotoFrame(action_data=self.action_data)
        elif self.code == 0x88:
            return ActionConstantPool(action_data=self.action_data)
        elif self.code == 0x8B:
            return ActionSetTarget(action_data=self.action_data)
        elif self.code == 0x8C:
            return ActionGoToLabel(action_data=self.action_data)
        elif self.code == 0x8D:
            return ActionWaitForFrame2(action_data=self.action_data)
        elif self.code == 0x9A:
            return ActionGetURL2(action_data=self.action_data)
        elif self.code == 0x9D:
            return ActionIf(action_data=self.action_data)
        elif self.code == 0x9F:
            return ActionGotoFrame2(action_data=self.action_data)
        elif self.code == 0x96:
            return ActionPush(action_data=self.action_data)
        else:
            print(self.code)
            return self

    def __repr__(self):
        ret = 'Action(%02X, %r, actions=%r)' % (self.code, self.length, self.action_data)
        return ret


class ButtonCondAction:
    def __init__(self, cond_action_size=None, cond_flag=0, actions=None):
        self.cond_action_size = cond_action_size
        self.cond_flag = cond_flag
        self.actions = actions

    def read_data(self, data):
        self.cond_action_size = struct.unpack_from('H', data)[0]
        offset = 2
        self.cond_flag = struct.unpack_from('H', data, offset)[0]
        offset += 2
        self.actions = list()
        while offset < len(data):
            action = Action()
            size = action.read_data(data[offset:])
            offset += size
            self.actions.append(action.analyze_action())

    def __repr__(self):
        ret = 'ButtonCondAction(actions=%r)' % self.actions
        return ret

    def __str__(self):
        ret = 'ButtonCondAction:\n  %s\n' % '\n  '.join(str(x) for x in self.actions)
        return ret


class ActionEnd(Action):
    def __init__(self):
        super().__init__(code=0)

    def __repr__(self):
        return 'ActionEnd()'


class ActionPlay(Action):
    def __init__(self):
        super().__init__(code=0x06)

    def __repr__(self):
        return 'ActionPlay()'


class ActionStop(Action):
    def __init__(self):
        super().__init__(code=0x07)

    def __repr__(self):
        return 'ActionStop()'


class ActionAdd(Action):
    def __init__(self):
        super().__init__(code=0x0A)

    def __repr__(self):
        return 'ActionAdd()'


class ActionEquals(Action):
    def __init__(self):
        super().__init__(code=0xE)

    def __repr__(self):
        return 'ActionEquals()'


class ActionLess(Action):
    def __init__(self):
        super().__init__(code=0xF)

    def __repr__(self):
        return 'ActionLess()'


class ActionNot(Action):
    def __init__(self):
        super().__init__(code=0x12)

    def __repr__(self):
        return 'ActionNot()'


class ActionPop(Action):
    def __init__(self):
        super().__init__(code=0x17)

    def __repr__(self):
        return 'ActionPop()'


class ActionGetVariable(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x1C)

    def __repr__(self):
        return 'ActionGetVariable()'


class ActionSetVariable(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x1D)

    def __repr__(self):
        return 'ActionSetVariable()'


class ActionCastOp(Action):
    def __init__(self):
        super().__init__(code=0x2B)

    def __repr__(self):
        return 'ActionAdd()'


class ActionCallFunction(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x3D)

    def __repr__(self):
        return 'ActionCallFunction()'


class ActionGotoFrame(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x81)

    def __repr__(self):
        return 'ActionSetTarget()'


class ActionConstantPool(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x88)

    def __repr__(self):
        return 'ActionConstantPool()'


class ActionSetTarget(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x8B)

    def __repr__(self):
        return 'ActionSetTarget()'


class ActionGoToLabel(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x8C)

    def __repr__(self):
        return 'ActionGoToLabel()'


class ActionWaitForFrame2(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x8D)

    def __repr__(self):
        return 'ActionWaitForFrame2()'


class ActionPush(Action):
    get_data = {
        0: lambda x: BasicData.read_string(x),
        1: lambda x: (struct.unpack_from('f', x)[0], 4),
        4: lambda x: (struct.unpack_from('B', x)[0], 1),
        5: lambda x: (struct.unpack_from('B', x)[0] != 0, 1),
        6: lambda x: (struct.unpack_from('d', x)[0], 8),
        7: lambda x: (struct.unpack_from('I', x)[0], 4),
        8: lambda x: (struct.unpack_from('B', x)[0], 1),
        9: lambda x: (struct.unpack_from('H', x)[0], 2),
    }

    def __init__(self, **kwargs):
        super().__init__(code=0x96)
        action_data = kwargs.get('action_data')
        if action_data is None:
            self.elements = kwargs.get('elements')
        else:
            self.elements = list()
            offset = 0
            while offset < len(action_data):
                data_type = struct.unpack_from('B', action_data[offset:])[0]
                offset += 1
                data, size = self.get_data[data_type](action_data[offset:])
                offset += size
                self.elements.append((data_type, data))

    def __repr__(self):
        return 'ActionPush(element=%r)' % self.elements


class ActionGetURL2(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x9A, length=1)

    def __repr__(self):
        return 'ActionGetURL2()'


class ActionIf(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x9D, length=2)

    def __repr__(self):
        return 'ActionIf()'


class ActionGotoFrame2(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x9F)

    def __repr__(self):
        return 'ActionWaitForFrame2()'
