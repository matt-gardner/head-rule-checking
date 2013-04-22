#!/usr/bin/env python

import os
from trees import Tree
from collections import defaultdict

error_counts = defaultdict(int)
error_category_counts = defaultdict(int)

def main(ptb_file, results_dir):
    correct_patterns = set()
    for root, dirs, files in os.walk(results_dir):
        for f in files:
            if 'correct_' not in f:
                continue
            for line in open(root + '/' + f):
                correct_patterns.add(line.strip()[1:-1])
    trees = []
    text = ''
    skipped = 0
    for line in open(ptb_file):
        if text and line[0] != ' ':
            try:
                trees.append(Tree.read(text))
            except AttributeError:
                #print text
                skipped += 1
            text = ''
        text += line
    if text:
        trees.append(Tree.read(text))
    good_trees = []
    for tree in trees:
        if tree_is_good(tree.root.children[0], correct_patterns):
            good_trees.append(tree)
    print 'Number of trees:', len(trees)
    print 'Number of good trees:', len(good_trees)
    print 'Skipped:', skipped
    cats = error_category_counts.keys()
    cats.sort(key=lambda x: error_category_counts[x])
    for cat in cats:
        print '%s: %d' % (cat, error_category_counts[cat])
    print
    errors = error_counts.keys()
    errors.sort(key=lambda x: error_counts[x], reverse=True)
    for error in errors[:30]:
        print '%s: %d' % (error, error_counts[error])
    out = open('good_trees.mrg', 'w')
    for tree in good_trees:
        out.write(tree.pretty())
        out.write('\n\n')


word_tags = set(['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS',
        'MD', 'NN', 'NNS', 'NNP', 'NNPS', 'PDT', 'POS', 'PRP', 'PRP$', 'RB',
        'RBR', 'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN',
        'VBP', 'VBZ', 'WDT', 'WP', 'WP$', 'WRB', ',', ':', '``', '.', '$',
        "''", '-LRB-', '-RRB-', '-NONE-'])

def tree_is_good(node, correct_patterns):
    if node.label in word_tags:
        # Always return true from a word tag
        return True
    if len(node.children) == 1:
        return tree_is_good(node.children[0], correct_patterns)
    parent_label = node.label
    if parent_label[0] != '-':
        parent_label = parent_label.split('-', 1)[0]
    pattern = parent_label
    for child in node.children:
        label = child.label
        if label[0] != '-':
            label = label.split('-', 1)[0]
        pattern += ' ' + label
    if pattern not in correct_patterns:
        error_counts[pattern] += 1
        error_category_counts[parent_label] += 1
        return False
    for child in node.children:
        if not tree_is_good(child, correct_patterns):
            return False
    return True



if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        ptb_file = sys.argv[1]
    else:
        ptb_file = '../PTB.MRG'
    main(ptb_file, 'results/')

# vim: et sw=4 sts=4
