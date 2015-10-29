class ActionState(object):
    def __init__(self, name, ordinal, permitted_transitions=set()):
        self.name = name
        self.ordinal = ordinal
        self.permitted_transitions = permitted_transitions
    def __cmp__(self, other):
        if isinstance(other, ActionState):
            return cmp(self.ordinal, other.ordinal)
        else:
            raise TypeError()
    def __repr__(self):
        return 'ActionState.{}'.format(self.name)

    @property
    def is_cancelable(self):
        return ActionState.CANCEL in self.permitted_transitions

ActionState.COMPLETE = ActionState('COMPLETE', 4)
ActionState.CANCEL = ActionState('CANCEL', 3)
ActionState.COOL_DOWN = ActionState('COOL_DOWN', 2, { ActionState.COMPLETE })
ActionState.WARM_UP = ActionState('WARM_UP', 1, { ActionState.COOL_DOWN, ActionState.CANCEL })
ActionState.NOT_STARTED = ActionState('NOT_STARTED', 0, { ActionState.WARM_UP, ActionState.CANCEL })


