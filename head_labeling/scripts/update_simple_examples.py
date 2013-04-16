#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'head_labeling.settings'
sys.path.append('.')
sys.path.append('../')

from django.db import transaction
from test_suite.models import *


@transaction.commit_manually
def main(category_symbol, simple_penn_file, simple_supa_file, inter_penn_file):
    category = Category.objects.get(symbol=category_symbol)
    suites = category.testsuite_set.all()
    # We just update the most recent version of the test suite
    test_suite = suites[suites.count()-1]
    expansions = test_suite.expansion_set.order_by('index')
    # We don't have simple supa yet, but we will
    supa_text = ''
    supa_texts = []
    line_number = 0
    for line in open(simple_supa_file):
        line_number += 1
        if line == '\n':
            if supa_text is None:
                supa_texts.append('')
                supa_text = ''
            elif supa_text == '':
                supa_text = None
            else:
                supa_texts.append(supa_text)
                supa_text = ''
            continue
        supa_text += str(line_number) + '\t' + line
    penn_text = ''
    penn_texts = []
    for line in open(simple_penn_file):
        if line == '\n':
            penn_texts.append(penn_text)
            penn_text = ''
            continue
        penn_text += line
    inter_penn_texts = []
    penn_text = ''
    for line in open(inter_penn_file):
        if line == '\n':
            inter_penn_texts.append(penn_text)
            penn_text = ''
            continue
        penn_text += line
    if (len(expansions) != len(penn_texts)
            or len(expansions) != len(supa_texts)
            or len(expansions) != len(inter_penn_texts)):
        print len(expansions), len(penn_texts)
        print len(expansions), len(supa_texts)
        print len(expansions), len(inter_penn_texts)
        print penn_texts[len(supa_texts)]
        raise RuntimeError('Error processing files')
    for i, expansion in enumerate(expansions):
        expansion.simple_supa_example = supa_texts[i]
        expansion.simple_penn_example = penn_texts[i]
        expansion.intermediate_penn_example = inter_penn_texts[i]
        expansion.save()
    transaction.commit()


if __name__ == '__main__':
    from import_suite import categories
    import sys
    base = sys.argv[1]
    if len(sys.argv) > 2:
        cats = sys.argv[2:]
    else:
        cats = categories
    for category in cats:
        cat_base = base + category + '/' + category
        simple_supa_file = cat_base + '_simple.supa'
        simple_penn_file = cat_base + '_PTBtrees_simple.mrg'
        inter_penn_file = cat_base + '_PTBtrees_intermediate.mrg'
        print 'Updating simple examples for test suite', category
        try:
            main(category, simple_penn_file, simple_supa_file, inter_penn_file)
        except:
            print 'Failed!'
            raise

# vim: et sw=4 sts=4
