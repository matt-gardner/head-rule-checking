#!/usr/bin/env python

from subprocess import Popen, PIPE

from trees import Tree, Node


def simplify_trees(suite_file, outfile):
    new_trees = []
    tree = ''
    for line in open(suite_file):
        if line == '\n':
            new_trees.append(convert_tree(Tree.read(tree)))
            tree = ''
        tree += line
    out = open(outfile, 'w')
    for tree in new_trees:
        out.write(tree.pretty())
        out.write('\n\n')


def convert_tree(tree):
    new_tree = tree.copy()
    for i in range(len(new_tree.root.children)):
        prune_node(new_tree.root.children[i])
    return new_tree


word_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS',
        'MD', 'NN', 'NNS', 'NNP', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR',
        'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP',
        'VBZ', 'WDT', 'WP', 'WP$', 'WRB']


def prune_node(node):
    if node.label in word_tags:
        return
    if node.label.startswith('NP'):
        prune_np(node)
        return
    if node.label.startswith('VP'):
        prune_vp(node)
        return
    for i in range(len(node.children)):
        prune_node(node.children[i])
    return


def prune_np(node):
    if node.children[0].label == '-NONE-':
        return
    else:
        if node.children[0].label == 'NNS':
            noun = node.children[0].children[0].label
        else:
            noun = 'students'
        node.children = []
        nns_node = Node('NNS', node, False)
        Node(noun, nns_node, True)
        return


def prune_vp(node):
    if node.children[0].label == 'VB':
        node.children = []
        vb_node = Node('VB', node, False)
        Node('break', vb_node, True)
        return
    elif node.children[0].label == 'VBD':
        node.children = []
        vbd_node = Node('VBD', node, False)
        Node('broke', vbd_node, True)
        return
    elif node.children[0].label == 'VBN':
        node.children = []
        vbn_node = Node('VBN', node, False)
        Node('broken', vbn_node, True)
        return
    elif node.children[0].label == 'VBZ':
        node.children = []
        vbz_node = Node('VBZ', node, False)
        Node('breaks', vbz_node, True)
        return
    elif node.children[0].label == 'VBG':
        node.children = []
        vbg_node = Node('VBG', node, False)
        Node('breaking', vbg_node, True)
        return
    elif node.children[0].label == 'VBP':
        node.children = []
        vbp_node = Node('VBP', node, False)
        Node('break', vbp_node, True)
        return


if __name__ == '__main__':
    from import_suite import categories
    import sys
    if len(sys.argv) > 1:
        cats = sys.argv[1].split(',')
    else:
        cats = categories
    for pos in cats:
        print 'Simplifying trees for category', pos
        simplify_trees('input_files/%s/%s_PTBtrees.mrg' % (pos, pos),
                'input_files/%s/%s_PTBtrees_simple.mrg' % (pos, pos))
    proc = Popen('./scripts/update_simple_supa.sh', shell=True)
    proc.wait()
    #print "Producing SUPA from this script doesn't work!"
    #print "Remember to run ./scripts/update_simple_supa.sh"


# vim: et sw=4 sts=4
