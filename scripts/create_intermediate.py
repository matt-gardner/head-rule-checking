#!/usr/bin/env python

# Takes a list of head-labeled trees, and a list of annotations for those
# trees, and gives an accuracy on the annotated trees.

from __future__ import division

import os
from trees import Tree

def main(category, suites_dir):
    tree_file = None
    for root, dirs, files in os.walk('.'):
        for f in files:
            if 'sierra_postop' in f:
                tree_file = f
    if not tree_file:
        print 'Could not find sierra_postop file!  Exiting...'
        exit(-1)
    trees = []
    patterns = []
    text = ''
    for line in open(tree_file):
        if line == 'null\n':
            print 'Null found!'
            trees.append(None)
            continue
        if line == '\n':
            trees.append(Tree.read(text))
            text = ''
            continue
        text += line
    new_trees = []
    for i, tree in enumerate(trees):
        # Clear off some of the extra processing that the SUPA pipeline adds
        if tree is None:
            new_trees.append('')
            continue
        root = tree.root.children[1]
        clear_extra_labels(root)
        new_trees.append(root)
    outfile = '../' + suites_dir + '/' + category + '/' + category
    outfile += '_PTBtrees_intermediate.mrg'
    out = open(outfile, 'w')
    for tree in new_trees:
        if tree:
            out.write(tree.pretty())
            out.write('\n\n')
        else:
            out.write('\n')
    out.close()


def clear_extra_labels(node):
    if node.label[0].isdigit() or node.label[0] == '_':
        node.label = node.label.split('__')[1]
    else:
        node.label = node.label.split('__')[0]
    for child in node.children:
        clear_extra_labels(child)


if __name__ == '__main__':
    import sys
    main(sys.argv[1], sys.argv[2])

# vim: et sw=4 sts=4
