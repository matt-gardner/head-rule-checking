#!/usr/bin/python

"""Simple script to prepend indices to terminals in bracketed parse trees.

Terminals ending with the value of SKIP_STR are passed over. This indicator is
added by running Tsurgeon opfile preIndexing.op, in which the pattern for
skippable terminals is defined.
"""

import re
import sys
import utils

# Double underscores do not appear in PTB-3 (WSJ) or PATB. If one appears in
# your treebank, you must use a different intra-token field separator here, and
# in the macros and operation files.

# "token" = any sequence of non-space symbols preceding a right parenthesis.
TOKEN_REGEX = re.compile(r'([^\s()]+)\)')

TOKEN_INDEX_START = 1
TOKEN_INDEX = TOKEN_INDEX_START
# NOTE: SKIP_STR must match the "skip" suffix appended in Tsurgeon opfile
# preIndexing.op.
SKIP_STR = '_SKIP'


def token_repl(matchobj):
    global TOKEN_INDEX
    token = matchobj.group(1)
    index = TOKEN_INDEX
    index_incr = 1
    # Don't prepend or increment the index if it's a token to skip.
    if token.endswith(SKIP_STR):
        token = token.replace(SKIP_STR, '')
        index = ''
        index_incr = 0
    token = '{0}{sep}{1})'.format(index, token, sep=utils.FIELD_SEP)
    TOKEN_INDEX += index_incr
    return token


def process_tree(tree):
    global TOKEN_INDEX
    TOKEN_INDEX = TOKEN_INDEX_START
    # Run token_repl on each token discovered.
    tree = TOKEN_REGEX.sub(token_repl, tree)
    return tree


def main(args):
    trees = utils.read_trees_from_file(args[0], handler=process_tree)
    for tree in trees:
        print tree


if __name__ == '__main__':
    main(sys.argv[1:])
