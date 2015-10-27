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

def distance(a, b):
    """
    My custom distance function for this universe where everything
    happens at 45- and 90-degree angles and diagonals are 1.5 units
    long instead of 1.414
    :param a:
    :param b:
    :return:
    """
    (dx, dy) = (abs(a_ - b_) for (a_, b_) in zip(a, b))
    return min(dx, dy) * 1.5 + abs(dx - dy)

def vec_add(a, b):
    return tuple(a_ + b_ for (a_, b_) in zip(a, b))

def vec_subtract(a, b):
    return tuple(a_ - b_ for (a_, b_) in zip(a, b))

def vec_interpolate(a, b, t):
    return map(lambda (a_, b_): (a_ * (1 - t) + b_ * t), zip(a, b))

def sign(x):
    try:
        return map(lambda x_: cmp(x_, 0), x)
    except TypeError:
        return cmp(x, 0)

def all_true(items):
    return reduce(lambda a, b: a and b, items)

def is_adjacent_vector(vector):
    return vector in [(-1, 0), (1, 0), (0, -1), (0, 1)]