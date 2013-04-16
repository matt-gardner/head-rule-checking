#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'head_labeling.settings'
sys.path.append('.')
sys.path.append('../')

from django.contrib.auth.models import User
from test_suite.models import *


def main():
    user = User.objects.get(username='matt')
    annotations = Annotation.objects.select_related().filter(user=user)
    total = 0
    conflicting = 0
    for a in annotations:
        total += 1
        e = a.expansion
        for e_a in e.annotation_set.all():
            if (a.head_correct != e_a.head_correct or
                    a.head_index != e_a.head_index):
                print e.test_suite.category.symbol, e.index,
                print e_a.user.username, a.user.username
                e_a.delete()
                conflicting += 1
    print total, conflicting


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
