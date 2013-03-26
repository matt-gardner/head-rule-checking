#!/usr/bin/env python

# This is meant to be a one-time script to automatically populate the
# head_index field in an Annotation, because it was added later.  Basically, if
# an annotation says that the head rule is correctly applied, we figure out
# which of the daughters is currently the head.

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append('.')

from django.db import transaction
from test_suite.models import *

from trees import Tree

@transaction.commit_manually
def main():
    annotations = Annotation.objects.select_related().filter(head_correct=True)
    for annotation in annotations:
        expansion = annotation.expansion
        root = None
        for i, line in enumerate(expansion.supa_example.split('\n')):
            if 'ROOT' in line:
                if root != None:
                    print 'Two roots found; skipping'
                    continue
                root = i
        if root == None:
            # Sometimes the SUPA is empty; testing on 3/20/2013 showed that was
            # the only time this happened
            continue
        tree = Tree.read(expansion.penn_example)
        head_index = None
        for i, child in enumerate(tree.root.children):
            if root in child.terminal_indices():
                head_index = i+1
                break
        if head_index:
            annotation.head_index = head_index
            annotation.save()
        else:
            print 'Head index not found...'
    transaction.commit()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
