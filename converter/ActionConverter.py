convert_action = {
    0x6: lambda x: [{'type': 6}],
    0xE: lambda x: [{'type': 14}],
    0x1D: lambda x: [{'type': 29}],
    0x8C: lambda x: [{'type': 140, 'label': x.label}],
    0x96: lambda push: [convert_action_push_element(x) for x in push.elements],
}


def convert(do_action):
    actions = do_action.actions
    swiffy_actions = list()
    for action in actions:
        code = action.code
        if code == 0:
            break
        elif code in convert_action.keys():
            ret = convert_action[code](action)
            for x in ret:
                swiffy_actions.append(x)
        else:
            raise Exception('no action 0x%x' % code)
    return {'type': 9, 'actions': swiffy_actions}


def convert_action_push_element(element):
    if element[0] < 8:
        return {'type': 305, 'value': element[1]}
    else:
        raise NotImplementedError
