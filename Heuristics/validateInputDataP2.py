"""
AMMM Project Heuristics
Instance file validator for the pipe-destruction problem.
"""

from AMMMGlobals import AMMMException


class ValidateInputData(object):
    @staticmethod
    def validate(data):
        for paramName in ['n', 'm', 'w', 'c', 't']:
            if paramName not in data.__dict__:
                raise AMMMException('Parameter/Set(%s) not contained in Input Data' % str(paramName))

        n = data.n
        if not isinstance(n, int) or (n <= 0):
            raise AMMMException('n(%s) has to be a positive integer value.' % str(n))

        m = data.m
        if not isinstance(m, int) or (m <= 0):
            raise AMMMException('m(%s) has to be a positive integer value.' % str(m))

        data.w = list(data.w)
        w = data.w
        if len(w) != m:
            raise AMMMException('Size of w(%d) does not match with value of m(%d).' % (len(w), m))
        for value in w:
            if not isinstance(value, (int, float)) or (value < 0):
                raise AMMMException('Invalid parameter value(%s) in w.' % str(value))

        data.c = list(data.c)
        c = data.c
        if len(c) != m:
            raise AMMMException('Size of c(%d) does not match with value of m(%d).' % (len(c), m))
        for value in c:
            if not isinstance(value, (int, float)) or (value < 0):
                raise AMMMException('Invalid parameter value(%s) in c.' % str(value))

        data.t = [list(row) for row in data.t]
        t = data.t
        if len(t) != n:
            raise AMMMException('Size of t(%d) does not match with value of n(%d).' % (len(t), n))
        for row in t:
            if len(row) != n:
                raise AMMMException('Row size of t(%d) does not match with value of n(%d).' % (len(row), n))

