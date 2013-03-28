#!/usr/bin/python

"""Script to convert PTB-style trees to SUPA dependency format.

Assumes the input tree has a first child whose children are dependency subtrees,
each of the form:
Tree(id__form__postag, [head__hform__hpos, deprel])
"""

from nltk import tree as tree_module
import sys
import utils

__author__ = 'Michael Deeringer (mjd2188@columbia.edu)'


def convert_to_supa(tree):
    # Sentence tokens, per http://ilk.uvt.nl/conll/#dataformat
    tokens = []
    for dep_tree in tree[0]:
        token_id, form, postag = dep_tree.node.split(utils.FIELD_SEP)
        head, hform, unused_hpostag = dep_tree[0].split(utils.FIELD_SEP)
        if not (token_id and head):
            # Either token_id or head is empty, so don't emit this dependency.
            continue
        # Dependency relation to the head.
        deprel = dep_tree[1]
        # Unused CoNLL format fields.
        lemma = cpostag = feats = phead = pdeprel = '_'
        # 11 fields.
        fields = [int(token_id),
                  form,
                  lemma,
                  cpostag,
                  postag,
                  feats,
                  int(head),
                  deprel,
                  phead,
                  pdeprel,
                  hform]
        tokens.append(fields)
    # Sort tokens by token ID.
    tokens.sort(key=lambda x: x[0])
    return '\n'.join('\t'.join(map(str, fields)) for fields in tokens)


def main(args):
    """Main method."""
    if len(args) != 1:
        raise ValueError('Invalid arguments to main(): {!s}. Can only take one '
                         'filename'.format(args))
    # TODO: support multiple input filenames
    trees = utils.read_trees_from_file(args[0])
    for i, tree in enumerate(trees, 1):
        if tree.startswith('null'):
            print >> sys.stderr, '***** ERROR: NULL TREE ({0}) *****'.format(i)
            print tree
            print
            continue
        tree_obj = tree_module.Tree(tree)
        supa_str = convert_to_supa(tree_obj)
        print supa_str
        print


if __name__ == '__main__':
    main(sys.argv[1:])
