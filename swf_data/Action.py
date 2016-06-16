import struct


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
            self.action_data = data[offset:(offset + self.length - 1)]
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
        elif self.code == 0xE:
            return ActionEquals()
        elif self.code == 0x12:
            return ActionNot()
        elif self.code == 0x1C:
            return ActionGetVariable()
        elif self.code == 0x1D:
            return ActionSetVariable()
        elif self.code == 0x8C:
            return ActionGoToLabel(action_data=self.action_data)
        elif self.code == 0x9A:
            return ActionGetURL2(action_data=self.action_data)
        elif self.code == 0x9D:
            return ActionIf(action_data=self.action_data)
        elif self.code == 0x96:
            return ActionPush(action_data=self.action_data)
        else:
            print(self.code)
            return self

    def __repr__(self):
            ret = 'Action(%r, %r, actions=%r)' % (self.code, self.length, self.action_data)
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
    def __init__(self, **kwargs):
        super().__init__(code=0)

    def __repr__(self):
        return 'ActionEnd()'


class ActionEquals(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0xE)

    def __repr__(self):
        return 'ActionEquals()'


class ActionNot(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x12)

    def __repr__(self):
        return 'ActionNot()'


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


class ActionPush(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x96)

    def __repr__(self):
        return 'ActionPush()'


class ActionGoToLabel(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x8C)

    def __repr__(self):
        return 'ActionGoToLabel()'


class ActionPlay(Action):
    def __init__(self, **kwargs):
        super().__init__(code=0x06)

    def __repr__(self):
        return 'ActionPlay()'
