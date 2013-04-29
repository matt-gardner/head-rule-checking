base=..
$base/supa_docs/sierra.sh \
    -morder $base/supa_docs/macros/ORDER.txt \
    -oporder $base/supa_docs/opfiles/ORDER_TS.txt \
    -treeFile $base/head_rule_testing/good_trees.mrg \
    >good_trees.supa
rm -f sierra_*
$base/supa_docs/sierra.sh \
    -morder $base/supa_docs/macros/ORDER.txt \
    -oporder $base/supa_docs/opfiles/ORDER_TS_COLLINS.txt \
    -treeFile $base/head_rule_testing/good_trees.mrg \
    >good_trees.collins
rm -f sierra_*

