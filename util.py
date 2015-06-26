from numpy import array

def immutableArray(iterable):
    a = array(iterable)
    a.flags.writeable = False
    return a
