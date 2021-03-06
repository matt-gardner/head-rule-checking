#!/usr/bin/env python

from subprocess import Popen, PIPE

from trees import Tree


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
    children = new_tree.root.children
    node_to_keep = -1
    for i in range(len(children)):
        if children[i].label.startswith('W') and '-' in children[i].label:
            if children[i].label.split('-')[-1].isdigit():
                node_to_keep = children[i].label.split('-')[-1]
    if node_to_keep != -1:
        for i in range(len(children)):
            mark_node(children[i], node_to_keep)
    for i in range(len(children)):
        prune_node(children[i])
    return new_tree


def mark_node(node, to_mark):
    if not node.label.startswith('WH') and node.label.endswith(to_mark):
        mark_parents(node)
    for child in node.children:
        mark_node(child, to_mark)


def mark_parents(node):
    node.to_keep = True
    if node.parent:
        mark_parents(node.parent)


word_tags = ['CC', 'CD', 'DT', 'EX', 'FW', 'IN', 'JJ', 'JJR', 'JJS', 'LS',
        'MD', 'NN', 'NNS', 'NNP', 'PDT', 'POS', 'PRP', 'PRP$', 'RB', 'RBR',
        'RBS', 'RP', 'SYM', 'TO', 'UH', 'VB', 'VBD', 'VBG', 'VBN', 'VBP',
        'VBZ', 'WDT', 'WP', 'WP$', 'WRB']


def prune_node(node):
    if node.label in word_tags:
        return
    elif node.label.startswith('ADJP'):
        prune_adjp(node)
    elif node.label.startswith('ADVP'):
        prune_advp(node)
    elif node.label.startswith('NP'):
        prune_np(node)
    elif node.label.startswith('QP'):
        prune_qp(node)
    elif node.label.startswith('S-') or node.label == 'S':
        prune_s(node)
    elif node.label.startswith('VP'):
        prune_vp(node)
    for i in range(len(node.children)):
        prune_node(node.children[i])
    return


def remove_children(to_remove, node):
    for child in to_remove:
        try:
            if child.to_keep:
                continue
        except AttributeError:
            if len(node.children) == 1:
                #print 'About to remove last child!'
                #print node.pretty(0)
                break
            node.children.remove(child)


def prune_adjp(node):
    to_remove = set()
    rbs = []
    for child in node.children:
        if 'PP' in child.label:
            to_remove.add(child)
            to_remove.add(child)
        if child.label in ['RB', 'RBR', 'RBS']:
            rbs.append(child)
        if child.label in ['ADVP', 'S', 'SBAR']:
            to_remove.add(child)
    remove_children(to_remove, node)
    # Remove RBs, but only if there is something else in the node
    if len(node.children) > len(rbs):
        for child in rbs:
            node.children.remove(child)


def prune_advp(node):
    to_remove = set()
    rbs = []
    for child in node.children:
        if 'PP' in child.label:
            to_remove.add(child)
        if child.label == 'RB':
            rbs.append(child)
    remove_children(to_remove, node)
    # If there is more than one RB, remove all but the last
    if len(rbs) > 1:
        for child in rbs[:-1]:
            node.children.remove(child)


def prune_np(node):
    to_remove = set()
    nns = []
    nps = []
    cds = []
    for child in node.children:
        if 'PP' in child.label:
            to_remove.add(child)
        if 'VB' in child.label:
            to_remove.add(child)
        if child.label in ['JJ', 'JJS', 'JJR', 'CC', 'SBAR', ',', 'VP', ':',
                "``", "''", 'QP', 'ADJP', 'RRC', 'S', 'PRN', 'RB']:
            to_remove.add(child)
        if child.label in ['NN', 'NNP', 'NNS', 'NNPS']:
            nns.append(child)
        if child.label.startswith('NP'):
            nps.append(child)
        if child.label == 'CD':
            cds.append(child)
    remove_children(to_remove, node)
    # If there is more than one NN, remove all but the last
    if len(nns) > 1:
        for child in nns[:-1]:
            node.children.remove(child)
    # And if there is more than one NP, remove all but the first
    if len(nps) > 1:
        for child in nps[1:]:
            node.children.remove(child)
    # Now, if there is an NP before an NN, remove the NP
    nns = []
    nps = []
    for i, child in enumerate(node.children):
        if child.label in ['NN', 'NNP', 'NNS', 'NNPS']:
            nns.append((i, child))
        if child.label.startswith('NP'):
            nps.append((i, child))
    if len(nns) > 0:
        last_nn = nns[-1][0]
        for np in nps:
            if np[0] < last_nn:
                node.children.remove(np[1])
    # Remove CDs, but only if there is something else in the node
    if len(node.children) > len(cds):
        for child in cds:
            node.children.remove(child)


def prune_qp(node):
    to_remove = set()
    cds = []
    for child in node.children:
        if child.label in ['DT', '$', 'JJ']:
            to_remove.add(child)
        if child.label == 'CD':
            cds.append(child)
    remove_children(to_remove, node)
    # If there is more than one CD, remove all but the last
    if len(cds) > 1:
        for child in cds[:-1]:
            node.children.remove(child)


def prune_s(node):
    to_remove = set()
    ss = []
    for child in node.children:
        if 'PP' in child.label:
            to_remove.add(child)
        if 'ADVP' in child.label:
            to_remove.add(child)
        if child.label == 'S':
            ss.append(child)
        if child.label in [',', 'CC']:
            to_remove.add(child)
    remove_children(to_remove, node)
    if len(ss) > 1:
        for child in ss[1:]:
            node.children.remove(child)


def prune_vp(node):
    to_remove = set()
    vps = []
    for child in node.children:
        if 'PP' in child.label:
            to_remove.add(child)
        if 'ADVP' in child.label:
            to_remove.add(child)
        if child.label == 'S' or child.label.startswith('S-'):
            to_remove.add(child)
        if child.label in [':', 'NP-TMP', 'NP-1', 'SBAR-PRP', ',', '``', "''",
                'CC', 'UCP', 'SBAR-TMP', 'SBAR-ADV']:
            to_remove.add(child)
        if child.label == 'VP':
            vps.append(child)
    remove_children(to_remove, node)
    if len(vps) > 1:
        for child in vps[1:]:
            node.children.remove(child)


if __name__ == '__main__':
    import sys
    print sys.path
    sys.path.append('.')
    sys.path.append('head_labeling/')
    from head_labeling.scripts.import_suite import categories
    base = sys.argv[1]
    if len(sys.argv) > 2:
        cats = sys.argv[2:]
    else:
        cats = categories
    for pos in cats:
        print 'Simplifying trees for category', pos
        simplify_trees(base + '%s/%s_PTBtrees.mrg' % (pos, pos),
                base + '%s/%s_PTBtrees_simple.mrg' % (pos, pos))
    #proc = Popen('./scripts/update_simple_supa.sh', shell=True)
    #proc.wait()
    print "Producing SUPA from this script doesn't work!"
    print "Remember to run ./scripts/update_simple_supa.sh"


# vim: et sw=4 sts=4
