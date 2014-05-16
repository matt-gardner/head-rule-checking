#!/usr/bin/env python

from __future__ import division
import random
from subprocess import Popen

def main(supa_file, collins_file, malt_jar, percent_training, num_folds):
    supa_trees = []
    read_tree_file(supa_file, supa_trees)
    print len(supa_trees), 'SUPA trees'
    collins_trees = []
    read_tree_file(collins_file, collins_trees)
    print len(collins_trees), 'Collins trees'
    print 'Removing incomplete trees'
    to_remove = []
    for i in range(len(supa_trees)):
        if is_bad(supa_trees[i]) or is_bad(collins_trees[i]):
            to_remove.append(i)
        elif len(supa_trees[i]) != len(collins_trees[i]):
            to_remove.append(i)
    to_remove.sort(reverse=True)
    for i in to_remove:
        supa_trees.pop(i)
        collins_trees.pop(i)
    if len(supa_trees) != len(collins_trees):
        print 'Error! Unequal number of trees:', len(supa_trees),
        print len(collins_trees)
    trees = zip(supa_trees, collins_trees)
    print 'Remaining trees:', len(trees)
    supa_scores = []
    collins_scores = []
    for i in range(num_folds):
        print 'Running fold', (i+1)
        random.shuffle(trees)
        print 'SUPA'
        s_score = run_test([x[0] for x in trees],
                           malt_jar,
                           percent_training,
                           'supa',
                           i)
        print 'COLLINS'
        c_score = run_test([x[1] for x in trees],
                           malt_jar,
                           percent_training,
                           'collins',
                           i)
        print 'Results:'
        supa_scores.append(s_score)
        collins_scores.append(c_score)
        print s_score, c_score
        print
    metrics = ['Unlabeled attachment score', 'Complete trees']
    for i, metric in enumerate(metrics):
        print '\n%s:' % metric
        supa_metric = [x[i] for x in supa_scores]
        collins_metric = [x[i] for x in collins_scores]
        p_value = paired_permutation_test(supa_metric, collins_metric)
        print 'Supa mean:', sum(supa_metric) / num_folds
        print 'Collins mean:', sum(collins_metric) / num_folds
        print 'P-value:', p_value


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


def run_test(trees, malt_jar, percent_training, method, split_num):
    train_filename = method + '_train'
    test_filename = method + '_test'
    parsed_file = method + '_predicted'
    model_name = method + '_model'
    eval_file = method + '_eval'
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
        Popen(('mv', f, 'results/%d_' % (split_num) + f)).wait()
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
    parser.add_option('', '--ptb',
            help='Test on all trees in PTB, instead of just good trees '
            '(requires the files ptb.supa and ptb.collins)',
            dest='ptb',
            action='store_true',
            )
    parser.add_option('', '--percent-training',
            help='Percent of data to use for training',
            dest='percent',
            default=.9,
            type='float',
            )
    parser.add_option('', '--num-splits',
            help='Number of times to (randomly) split the data into training '
            'and test sets',
            dest='splits',
            default=10,
            type='int',
            )
    parser.add_option('', '--malt-jar',
            help='Location of the maltparser jar file',
            dest='malt_jar',
            default='../maltparser-1.7.2/maltparser-1.7.2.jar',
            )
    opts, args = parser.parse_args()
    supa_file = 'good_trees.supa'
    collins_file = 'good_trees.collins'
    if opts.ptb:
        supa_file = 'ptb.supa'
        collins_file = 'ptb.collins'
    main(supa_file, collins_file, opts.malt_jar, opts.percent, opts.splits)


# vim: et sw=4 sts=4
