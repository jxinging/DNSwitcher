# coding: utf8
__author__ = 'JinXing'

from setuptools import setup


setup(
    name='SmartDns',
    version='0.01',
    description='',
    author='jinxing',
    author_email='jxinging@gmail.com',
    packages=['smartdns'],
	data_files=[('/etc/', ['smartdns-example.json'])],
    long_description="",

    install_requires=['ping'],
    entry_points={
        "console_scripts": [
            "smartdns = smartdns:main"
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
