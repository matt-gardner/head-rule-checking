head-rule-checking
==================

A simple Django app for going over head rules as part of a treebanking project,
trying to make better head rules for conversion from a Penn Treebank
constituency parse to a dependency parse.

## User Guide

### Dependencies

Before beginning, be sure that you have Django and Django-South install on your
system.

### Using the app to annotate

TODO: write this section

### Dump current annotations from the app into text files

From the `head_labeling` directory, run the following command:

    python scripts/dump_annotations.py

This should update the annotations file in the `annotations` directory.

### Test current head rules against current annotations

From the `head_rule_testing` directory, run the following command:

    ./run_tests.sh [NP] [WHNP] [PP] [etc.]

As shown, you can list any phrase symbol or set of symbols to test only a
subset of the test suites.  If no symbols are given, all of them are tested.
The results appear in the `head_rule_testing/results` directory, with
`results.tsv` containing overall statistics, and `correct_*.tsv` and
`errors_*.tsv` giving specific annotations that pass or fail for each symbol.

`results.tsv` has 11 columns.  Those columns are:

1. The non-terminal symbol that was tested (e.g., `ADJP` or `QP`)
2. The number of expansion patterns seen for the non-terminal symbol (e.g.,
   (NP JJ NN))
3. The number of expansion patterns that have an annotation (as found in the
   `annotations/` directory)
4. The percent of patterns that have been annotated (i.e., (3) / (2))
5. The number of patterns that the head rules got correct, according to the
   annotations.
6. The percent of annotated patterns that were correct (i.e., (5) / (3))
7. The number of times the non-terminal in seen in the treebank (hereafter
   "tokens")
8. Number of tokens whose expansion pattern has an annotation
9. Percent of tokens that have been annotated (i.e., (8) / (7))
10. Number of tokens whose expansion was marked as correct
11. Percent of tokens marked correct (i.e., (10) / (8))

### Finding good trees in the Penn Treebank

It is important that you run `run_tests.sh` above before continuing to this
step, as this step uses the `correct_*.tsv` files produced by `run_tests.sh`.
You also need to have the Penn Treebank file that you wish to scour for good
trees available; the PTB is not distributed with this app for copyright
reasons.

If you run

    python get_good_trees.py [PennTreebank_file]

you will get output containing statistics of how many trees were found that
consisted only of patterns marked as correct, and which patterns caused the
most trees to be marked as bad.  If you do not pass a parameter to the script,
the path to the PTB file will default to `../PTB.MRG`.

This command will also produce a file called `good_trees.mrg`.  This file
consists of the trees that were found to be completely correct, as they were in
the original file (though perhaps with some reformatting).  This file is fit to
be used to produce SUPA output, as shown in the next section.

### Producing SUPA for good trees

From the same directory (`head_rule_labeling/`), the following command will
generate `good_trees.supa`, containing SUPA output for the good trees:

    ../supa_docs/sierra.sh -morder ../supa_docs/macros/ORDER.txt -oporder ../supa_docs/opfiles/ORDER_TS.txt -treeFile good_trees.mrg >good_trees.supa

It will also produce three `sierra_*` files that can be erased with `rm -f
sierra_*`.

This SUPA file is compatible with the CoNLL format, and thus is suitable to be
used for training MaltParser.

There is one thing to note, here, though.  The SUPA generation script sometimes
leaves `null` values for a sentence (i.e., `good_trees.supa` has a line that
begins and ends with `null` instead of the typical CoNLL format).  If this
happens, it will cause a NullPointerException when training MaltParser, and
thus those lines need to be removed.  There is not currently a script to do
that, so it must be done by hand.

### Training MaltParser from SUPA

To train MaltParser, be sure that you first have downloaded and extracted
MaltParser from [maltparser.org](http://www.maltparser.org/install.html).  Then
you can follow the instructions on the [User
Guide](http://www.maltparser.org/userguide.html), which are repeated here for
convenience.

To train the parser using `good_trees.supa`, from the `head_rule_testing/`
directory:

    java -jar /path/to/maltparser/maltparser-1.7.2.jar -c test -i good_trees.supa -m learn

This will create a MaltConfiguration file (which contains a learned model)
called `test.mco`.  If you change the parameter after `-c` in the command
above, you can change the name of this output file.

### Testing the MaltParser

All I have so far is a command to parse CoNLL-formatted data.  I don't have a
script to produce a separate training/testing split, nor to evaluate the
parses made by MaltParser.  To run the parser on `good_trees.supa`, you run the
following command:

    java -jar /path/to/maltparser/maltparser-1.7.2.jar -c test -i good_trees.supa -o parsed.conll -m parse

where the output will be stored in `parsed.conll`.  The parameter value for
`-c` must match that given during the training step.
