"""
Force import of all modules in this package in order to get the standard test
runner to pick up the tests.  Yowzers.
"""
from __future__ import unicode_literals
import os
import django

modules = [filename.rsplit('.', 1)[0]
           for filename in os.listdir(os.path.dirname(__file__))
           if filename.endswith('.py') and not filename.startswith('_')
           and not filename.startswith('.#')]  # emacs files?
__test__ = dict()

if django.VERSION < (1, 6):
    for module in modules:
        exec("from djangorpc.tests.%s import *" % module)
