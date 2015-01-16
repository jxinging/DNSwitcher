# coding: utf8
__author__ = 'JinXing'

from json import load

_CONFIG = None


def load_config(json_file, reload_=False):
    global _CONFIG
    if _CONFIG is None or reload_:
        _CONFIG = load(open(json_file))
    return _CONFIG


def get(key):
    return _CONFIG.get(key)