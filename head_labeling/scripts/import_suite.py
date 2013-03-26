#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'head_labeling.settings'
sys.path.append('.')
sys.path.append('../')

from django.db import transaction
from test_suite.models import *

categories = ['ADJP', 'ADVP', 'CONJP', 'FRAG', 'INTJ', 'LST', 'NAC', 'NP',
        'NX', 'PP', 'PRN', 'PRT', 'QP', 'RRC', 'S', 'SBAR', 'SBARQ',
        'SINV', 'SQ', 'UCP', 'VP', 'WHADJP', 'WHADVP', 'WHNP', 'WHPP', 'X']


@transaction.commit_manually
def main(category_symbol, grouped_file, supa_file, penn_file):
    try:
        category = Category.objects.get(symbol=category_symbol)
    except Category.DoesNotExist:
        category = Category(symbol=category_symbol)
        category.save()
    suites = category.testsuite_set.all()
    if len(suites) == 0:
        test_suite = TestSuite(category=category, version=1)
    else:
        prev_version = suites.order_by('version')[len(suites)-1].version
        test_suite = TestSuite(category=category, version=prev_version+1)
    test_suite.save()
    expansions = []
    for i, line in enumerate(open(grouped_file)):
        count, rule, _ = line.split('\t')
        expansions.append(ExpansionData(test_suite, count, rule, i+1))
    supa_text = ''
    supa_texts = []
    line_number = 0
    for line in open(supa_file):
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
    for line in open(penn_file):
        if line == '\n':
            penn_texts.append(penn_text)
            penn_text = ''
            continue
        penn_text += line
    if (len(expansions) != len(supa_texts)
            or len(expansions) != len(penn_texts)):
        raise RuntimeError('Error processing files')
    for i, expansion in enumerate(expansions):
        expansion.supa_example = supa_texts[i]
        expansion.penn_example = penn_texts[i]
        expansion.save()
    transaction.commit()


class ExpansionData(object):
    def __init__(self, test_suite, count, rule, index):
        self.test_suite = test_suite
        self.rule = rule
        self.count = count
        self.index = index
        self.supa_example = None
        self.penn_example = None

    def save(self):
        if self.supa_example is None or self.penn_example is None:
            raise SomeNastyError()
        e = Expansion(test_suite=self.test_suite, rule=self.rule,
                supa_example=self.supa_example, penn_example=self.penn_example,
                count=self.count, index=self.index)
        e.save()


if __name__ == '__main__':
    base = 'input_files/'
    for category in categories:
        cat_base = base + category + '/' + category
        grouped_file = cat_base + '_tagAsParent_rules_grouped.txt'
        supa_file = cat_base + '.supa'
        penn_file = cat_base + '_PTBtrees.mrg'
        print 'Importing test suite for category', category
        main(category, grouped_file, supa_file, penn_file)

# vim: et sw=4 sts=4
