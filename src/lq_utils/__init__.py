# -*- coding: utf-8 -*-

__author__="lreqc"
__date__ ="$2009-08-06 21:53:13$"

def raw(arg=''):
    # string in both 2.x and 3.x
    if isinstance(arg, bytes):
        return arg
    else:
        return arg.encode('utf-8')