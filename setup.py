# coding: utf8
__author__ = 'JinXing'

from setuptools import setup


setup(
    name='DNSwitcher',
    version='0.02',
    description='smart dns switcher',
    author='jinxing',
    author_email='jxinging@gmail.com',
    url="https://github.com/jinxingxing/DNSwitcher",
    packages=['dnswitcher'],
    data_files=[('', ['dnswitcher-example.json'])],
    long_description="",

    install_requires=[],
    entry_points={
        "console_scripts": [
            "dnswitcher = dnswitcher:main"
        ]
    }
)

# import os
# import sys
# dnspod_python_setup = os.path.join(os.path.abspath(os.path.dirname(__file__)),
#                                    "dnspod-python/setup.py")
# ret = os.system("cd %s && python %s install" % (
#     os.path.dirname(dnspod_python_setup), dnspod_python_setup))
# if ret != 0:
#     sys.exit(ret)
