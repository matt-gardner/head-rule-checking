#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'head_labeling.settings'
sys.path.append('.')
sys.path.append('../')

from django.contrib.auth.models import User
from test_suite.models import *

# vim: et sw=4 sts=4
