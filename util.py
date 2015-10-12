"""Assorted functions which don't belong anywhere else"""

from numpy import array

def immutableArray(iterable):
    a = array(iterable)
    a.flags.writeable = False
    return a

def removeAdjacentDuplicates(a_list):
    return reduce(
        lambda stack, elem:
            stack + [elem]
            if len(stack) == 0 or stack[-1] != elem
            else stack,
        [[]] + a_list
    )

def logging_passthru(arg, message_template):
    print message_template.format(arg)
    return arg

def resolution_pair(width_x_height):
    """Casts a resolution string such as "1024x768" to a pair of integers"""
    width, height = width_x_height.split('x')
    return int(width), int(height)
