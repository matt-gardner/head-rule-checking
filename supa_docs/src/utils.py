#!/usr/bin/python

from nltk.tokenize import sexpr_tokenize

# Constants to export.
FIELD_SEP = '__'


def read_trees_from_file(filename, handler=None):
    with open(filename, 'r') as infile:
        file_str = infile.read()
        # The list returned by sexpr_tokenize may contain whitespace strings.
        tree_strs = [tree for tree in sexpr_tokenize(file_str)
                     if not tree.isspace()]
    return map(handler, tree_strs)
