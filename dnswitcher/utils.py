# coding: utf8
__author__ = 'JinXing'

from config import get


def pdebug(format_, *args):
    if get("debug"):
        print (format_ % args).encode('utf8')


def plog(format_, *args):
    print (format_ % args).encode('utf8')