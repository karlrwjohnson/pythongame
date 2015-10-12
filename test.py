
def describe(thing):
    thing_repr = repr(thing)
    print thing_repr
    print '-' * len(thing_repr)
    for attr_name in dir(thing):
        print " - {} : {}".format(attr_name, repr(getattr(thing, attr_name)))

class FakeObservable (object):
    print "FakeObservable says hi"
    def __init__(self):
        print "FakeObservable.__init__() says hi"

class EventType (object):
    print "EventType says hi"
    def __init__(self, prototype_function):
        self.prototype_function = prototype_function

    def __str__(self):
        return self.prototype_function.func_name

    def __repr__(self):
        return 'EventType({})'.format(self.prototype_function.func_name)

    def matches_signature(self, function):
        # Compare argument lengths for now
        return self.prototype_function.func_code.co_argcount == function.func_code.co_argcount

class Foo (FakeObservable):
    print "Foo says hi"

    @EventType
    def BAR_CHANGE (foo, oldbar):
        pass

    def __init__(self):
        super(Foo, self).__init__()
        pass

foo = Foo()

print repr(Foo.BAR_CHANGE)
describe(Foo.BAR_CHANGE.prototype_function)
describe(Foo.BAR_CHANGE.prototype_function.func_code)
print "IS INSTANCE" if isinstance(Foo.BAR_CHANGE, EventType) else "IS NOT INSTANCE"
