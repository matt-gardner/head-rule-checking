#!/usr/bin/env python

# Takes a list of head-labeled trees, and a list of annotations for those
# trees, and gives an accuracy on the annotated trees.

from __future__ import division

import os
from trees import Tree

def main(annotation_file, category):
    outfile = 'results/results.tsv'
    tree_file = None
    for root, dirs, files in os.walk('.'):
        for f in files:
            if 'sierra_postop' in f:
                tree_file = f
    if not tree_file:
        print 'Could not find sierra_postop file!  Exiting...'
        exit(-1)
    annotations = {}
    annotation_patterns = {}
    for line in open(annotation_file):
        if line.startswith('index'): continue
        index, pattern, head_index = line.strip().split('\t')
        annotations[int(index)] = int(head_index) - 1
        annotation_patterns[pattern] = int(head_index) - 1
    trees = []
    patterns = []
    text = ''
    for line in open(tree_file):
        if line == 'null\n':
            trees.append(None)
            continue
        if line == '\n':
            trees.append(Tree.read(text))
            text = ''
            continue
        text += line
    count_file = '../test_suites_v2/%s/%s_tagAsParent_rules_grouped.txt' % (
            category, category)
    counts = []
    i = 0
    for line in open(count_file):
        count, pattern, _ = line.split('\t')
        counts.append(int(count))
        # TODO: this could be better - like check the annotation file to be
        # sure that the patterns match
        patterns.append(pattern)
        i += 1
    if len(counts) != len(trees):
        print 'Error! Incorrect alignment between trees and counts:'
        print len(counts), len(trees)
        exit(-1)
    # 'count' is token count, 'num' is type count
    total_count = 0
    count_annotated = 0
    count_correct = 0
    num_patterns = 0
    num_annotated = 0
    num_correct = 0
    errors = []
    correct = []
    for i, tree in enumerate(trees):
        pattern = patterns[i]
        num_patterns += 1
        total_count += counts[i]
        index = i + 1
        if index not in annotations: continue
        num_annotated += 1
        count_annotated += counts[i]

        # Clear off some of the extra processing that the SUPA pipeline adds
        if tree is None:
            continue
        root = tree.root.children[1]
        head = root.label.split('__', 1)[1]
        head_index = -1

        # The labels are on trees that haven't had WH-movement undone - we have
        # to correct the annotations for that.  This isn't perfect, but it will
        # do for now.
        annotated_children = len(pattern.split()) - 1
        actual_children = len(root.children)
        is_conjpp = 'CONJPP' in [x.label.split('__')[0] for x in root.children]
        if not is_conjpp and actual_children == annotated_children - 1:
            annotations[index] = annotations[index] - 1

        # Now to actually check to see what was labeled as the head
        for j, child in enumerate(root.children):
            child_head = child.label.split('__', 1)[1]
            if child_head == head:
                head_index = j + 1
                if j == annotations[index]:
                    correct.append(patterns[i])
                    num_correct += 1
                    count_correct += counts[i]
                    break
        else:
            errors.append((patterns[i], head_index, annotations[index]+1))
    percent_tested = num_annotated / num_patterns
    percent_correct = num_correct / num_annotated
    count_percent_annotated = count_annotated / total_count
    count_percent_correct = count_correct / count_annotated
    out = open(outfile, 'a')
    out.write('%s\t%d\t%d\t%.3f\t%d\t%.3f\t%d\t%d\t%.3f\t%d\t%.3f\n' % (
            category, num_patterns, num_annotated, percent_tested, num_correct,
            percent_correct, total_count, count_annotated,
            count_percent_annotated, count_correct, count_percent_correct))
    error_file = open('results/errors_%s.tsv' % category, 'w')
    error_file.write('pattern\tmarked\tactual\n')
    for error in errors:
        error_file.write('%s\t%d\t%d\n' % error);
    correct_file = open('results/correct_%s.tsv' % category, 'w')
    for pattern in correct:
        correct_file.write('%s\n' % pattern);


if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])

# vim: et sw=4 sts=4
