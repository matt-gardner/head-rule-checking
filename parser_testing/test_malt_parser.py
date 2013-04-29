#!/usr/bin/env python

import random
from subprocess import Popen

def main(supa_file, collins_file, malt_jar, percent_training, num_folds):
    supa_trees = []
    read_tree_file(supa_file, supa_trees)
    collins_trees = []
    read_tree_file(collins_file, collins_trees)
    if len(supa_trees) != len(collins_trees):
        print 'Error! Unequal number of trees:', len(supa_trees),
        print len(collins_trees)
    trees = zip(supa_trees, collins_trees)
    supa_scores = []
    collins_scores = []
    for i in range(num_folds):
        print 'Running fold', (i+1)
        random.shuffle(trees)
        print 'SUPA'
        s_score = run_test([x[0] for x in trees], malt_jar, percent_training)
        print 'COLLINS'
        c_score = run_test([x[1] for x in trees], malt_jar, percent_training)
        print 'Results:'
        supa_scores.append(s_score)
        collins_scores.append(c_score)
        print s_score, c_score
        print
    p_value = paired_permutation_test(supa_scores, collins_scores)
    print 'Supa mean:', sum(supa_scores) / num_folds
    print 'Collins mean:', sum(collins_scores) / num_folds
    print 'P-value:', p_value


def read_tree_file(tree_file, trees):
    tree = ''
    for line in open(tree_file):
        if line == 'null\n':
            continue
        if line == '\n':
            if tree and not tree.isspace():
                trees.append(tree)
            tree = ''
        else:
            tree += line
    if tree:
        trees.append(tree)


def run_test(trees, malt_jar, percent_training):
    train_filename = 'train.supa'
    test_filename = 'test.supa'
    parsed_file = 'test.conll'
    model_name = 'test'
    eval_file = 'out.txt'
    train_file = open(train_filename, 'w')
    test_file = open(test_filename, 'w')
    num_training = percent_training * len(trees)
    for i, tree in enumerate(trees):
        if i < num_training:
            train_file.write(tree + '\n')
        else:
            test_file.write(tree+'\n')
    train_file.close()
    test_file.close()
    command = ['java', '-jar', malt_jar, '-c', model_name, '-i',
            train_filename, '-m', 'learn']
    dev_null = open('/dev/null')
    print 'Training MaltParser'
    proc = Popen(command, stdout=dev_null, stderr=dev_null)
    proc.wait()
    command = ['java', '-jar', malt_jar, '-c', model_name, '-i',
            test_filename, '-o', parsed_file, '-m', 'parse']
    print 'Testing MaltParser'
    proc = Popen(command, stdout=dev_null, stderr=dev_null)
    proc.wait()
    command = ['perl', 'eval.pl', '-g', test_filename, '-s', parsed_file, '-b',
            '-q', '-o', eval_file]
    print 'Evaluating results'
    proc = Popen(command, stdout=dev_null, stderr=dev_null)
    proc.wait()
    for line in open(eval_file):
        if 'Unlabeled attachment score' in line:
            score = float(line.split('=')[1].split('%')[0].strip())
    command = ['rm', '-f', train_filename, test_filename, parsed_file,
            eval_file, model_name+'.mco']
    proc = Popen(command)
    proc.wait()
    return score


def paired_permutation_test(data1, data2):
    """Performs an exact a paired permutation test.

    We create an array of the signed difference between the two data points,
    find the mean difference, and then test for all possible permutations of
    the signs if the new mean difference is higher than the original mean
    difference.
    """
    if len(data1) != len(data2):
        raise ValueError('This is a _paired_ test and you gave me data with'
                ' unequal lengths!')
    from itertools import izip
    diffs = [x-y for x,y in izip(data1, data2)]
    length = len(diffs)
    mean_diff = abs(sum(diffs)/length)
    n = 0
    for i in range(2**len(diffs)):
        a = i
        index = 1
        diff = 0
        while index <= length:
            if a%2 == 1:
                diff -= diffs[-index]
            else:
                diff += diffs[-index]
            if a > 0:
                a = a>>1
            index += 1
        diff = abs(diff/length)
        if diff >= mean_diff:
            n += 1
    return n/float(2**len(diffs))


if __name__ == '__main__':
    malt_jar = '../maltparser-1.7.2/maltparser-1.7.2.jar'
    main('good_trees.supa', 'good_trees.collins', malt_jar, .9, 10)


# vim: et sw=4 sts=4
