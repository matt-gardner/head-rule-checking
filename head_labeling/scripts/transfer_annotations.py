#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'head_labeling.settings'
sys.path.append('.')
sys.path.append('../')

from django.db import transaction
from test_suite.models import *

from difflib import SequenceMatcher


@transaction.commit_manually
def main(category_symbol):
    category = Category.objects.get(symbol=category_symbol)
    suites = category.testsuite_set.all()
    if len(suites) <= 1:
        'Less than two versions for category', category_symbol
        transaction.commit()
        return
    else:
        prev_version = suites.order_by('version')[len(suites)-2]
        new_version = suites.order_by('version')[len(suites)-1]
    prev_expansions = list(prev_version.expansion_set.order_by('index'))
    new_expansions = list(new_version.expansion_set.order_by('index'))
    for i, expansion in enumerate(prev_expansions):
        if supa_changed(expansion.supa_example,
                new_expansions[i].supa_example):
            continue
        for old_a in expansion.annotation_set.all():
            user = old_a.user
            try:
                new_expansions[i].annotation_set.get(user=user)
            except Annotation.DoesNotExist:
                new_a = Annotation(user=user, expansion=new_expansions[i],
                        head_index=old_a.head_index,
                        head_correct=old_a.head_correct,
                        comp_head_correct=old_a.comp_head_correct,
                        notes=old_a.notes)
                new_a.save()
    transaction.commit()

def supa_changed(a, b):
    s = SequenceMatcher(a=a, b=b)
    a_end = -1
    b_end = -1
    for a_begin, b_begin, length in s.get_matching_blocks():
        if length == 0: continue
        if a_end != -1:
            a_skipped = a[a_end:a_begin]
            b_skipped = b[b_end:b_begin]
            if a_skipped == '' and b_skipped == '-DO':
                pass
            elif a_skipped == '???' and b_skipped == 'OBJ-DO':
                pass
            else:
                return True
                break
        a_end = a_begin + length
        b_end = b_begin + length
    return False


if __name__ == '__main__':
    from import_suite import categories
    import sys
    if len(sys.argv) > 1:
        cats = sys.argv[1:]
    else:
        cats = categories
    for category in cats:
        print 'Transferring annotations for category', category
        main(category)

# vim: et sw=4 sts=4
