#!/usr/bin/env python

import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
sys.path.append('.')

from collections import defaultdict

from test_suite.models import *

def main():
    test_suites = defaultdict(lambda: defaultdict(list))
    lastest_version = defaultdict(int)
    for suite in TestSuite.objects.all():
        if suite.version > latest_version[suite.category.symbol]:
            latest_version[suite.category.symbol] = suite.version
    annotations = Annotation.objects.all()
    for annotation in annotations:
        expansion = annotation.expansion
        version = expansion.test_suite.version
        category = expansion.test_suite.category.symbol
        if version < latest_version[category]:
            continue
        test_suites[category][(expansion.index, expansion.rule)].append(
                annotation.head_index)
    annotation_dir = '../annotations/'
    for suite in test_suites:
        out = open(annotation_dir + suite + '_annotations.tsv', 'w')
        out.write('index\tpattern\thead_index\n')
        expansions = test_suites[suite].keys()
        expansions.sort()
        for expansion in expansions:
            labels = test_suites[suite][expansion]
            if 0 in labels:
                continue
            if labels.count(labels[0]) != len(labels):
                # Only output if all of the labels are the same - could
                # probably use some tweaking, but ok for now. TODOLATER
                continue
            out.write('%d\t%s\t%d\n' % (expansion[0], expansion[1], labels[0]))
        out.close()


if __name__ == '__main__':
    main()

# vim: et sw=4 sts=4
