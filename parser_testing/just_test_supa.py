#!/usr/bin/env python

from __future__ import division
from subprocess import Popen

def main(malt_jar, training_file, testing_file):
    training_trees = []
    read_tree_file(training_file, training_trees)
    print len(training_trees), 'training trees'
    testing_trees = []
    read_tree_file(testing_file, testing_trees)
    print len(testing_trees), 'testing trees'
    print 'Removing incomplete trees'
    to_remove = []
    for i in range(len(training_trees)):
        if is_bad(training_trees[i]):
            to_remove.append(i)
    to_remove.sort(reverse=True)
    print len(training_trees), 'training trees'
    for i in to_remove:
        training_trees.pop(i)
    to_remove = []
    for i in range(len(testing_trees)):
        if is_bad(testing_trees[i]):
            to_remove.append(i)
    to_remove.sort(reverse=True)
    for i in to_remove:
        testing_trees.pop(i)
    print len(testing_trees), 'testing trees'

    score = run_test(training_trees, testing_trees, malt_jar)
    metrics = ['Unlabeled attachment score', 'Complete trees']
    for i, metric in enumerate(metrics):
        print '\n%s:' % metric
        print score[i]


def read_tree_file(tree_file, trees):
    tree = ''
    for line in open(tree_file):
        if line == 'null\n':
            trees.append('')
            continue
        if line == '\n' and tree:
            trees.append(tree)
            tree = ''
        else:
            tree += line
    if tree:
        trees.append(tree)


def is_bad(tree):
    if not tree:
        return True
    for i, line in enumerate(tree.split('\n')):
        if line and int(line.split('\t')[0]) != i+1:
            return True
    return False


def run_test(training_trees, testing_trees, malt_jar):
    method = 'ptb_test_'
    train_filename = method + '_train'
    test_filename = method + '_test'
    parsed_file = method + '_predicted'
    model_name = method + '_model'
    eval_file = method + '_eval'
    train_file = open(train_filename, 'w')
    test_file = open(test_filename, 'w')
    for tree in training_trees:
        train_file.write(tree + '\n')
    for tree in testing_trees:
            test_file.write(tree+'\n')
    train_file.close()
    test_file.close()
    command = ['java', '-Xmx4g', '-jar', malt_jar, '-c', model_name, '-i',
            train_filename, '-m', 'learn']
    print 'Training MaltParser'
    proc = Popen(command)#, stdout=dev_null, stderr=dev_null)
    proc.wait()
    command = ['java', '-Xmx4g', '-jar', malt_jar, '-c', model_name, '-i',
            test_filename, '-o', parsed_file, '-m', 'parse']
    print 'Testing MaltParser'
    proc = Popen(command)#, stdout=dev_null, stderr=dev_null)
    proc.wait()
    command = ['perl', 'eval.pl', '-g', test_filename, '-s', parsed_file, '-b',
            '-q', '-o', eval_file]
    print 'Evaluating results'
    proc = Popen(command)#, stdout=dev_null, stderr=dev_null)
    proc.wait()
    total_sentences = 0
    correct_sentences = 0
    for line in open(eval_file):
        if 'Unlabeled attachment score' in line:
            ula_score = float(line.split('=')[1].split('%')[0].strip())
        else:
            fields = line.strip().split()
            if fields and fields[0].isdigit():
                total_sentences += 1
                if fields[4] == '100.00':
                    correct_sentences += 1
    percent_correct = correct_sentences / total_sentences
    Popen(('mkdir', '-p', 'results')).wait()
    for f in [train_filename, test_filename, parsed_file, eval_file,
              model_name+'.mco']:
        Popen(('mv', f, 'results/' + f)).wait()
    return (ula_score, percent_correct)


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
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option('', '--training',
            dest='training',
            )
    parser.add_option('', '--testing',
            dest='testing',
            )
    parser.add_option('', '--malt-jar',
            help='Location of the maltparser jar file',
            dest='malt_jar',
            default='../maltparser-1.7.2/maltparser-1.7.2.jar',
            )
    opts, args = parser.parse_args()
    main(opts.malt_jar, opts.training, opts.testing)


# vim: et sw=4 sts=4
