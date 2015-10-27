"""
Patches pickling to support instance methods (i.e. functions attached to objects)
"""

import copy_reg

def get_instancemethod_type():
    class AClass(object):
        def a_method(self):
            pass
    return type(AClass().a_method)

def unpickle_instancemethod(method_class, method_object, method_name):
    #TODO: Get the method defined on the CLASS, in case a child class overrode it.
    return getattr(method_object, method_name)

def pickle_instancemethod(method):
    method_class = method.im_class
    method_object = method.im_self
    method_name = method.im_name
    return unpickle_instancemethod, (method_class, method_object, method_name)

copy_reg.pickle(get_instancemethod_type(), pickle_instancemethod)
