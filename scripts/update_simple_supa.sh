if [ $1 ]; then
    i=1
    while true; do
        if [ $1 ]; then
            cats[$i]=$1
            shift
        else
            break
        fi
        i=$i+1
    done
else
    cats=('ADJP' 'ADVP' 'CONJP' 'FRAG' 'INTJ' 'LST' 'NAC' 'NP' 'NX' 'PP' \
        'PRN' 'PRT' 'QP' 'RRC' 'S' 'SBAR' 'SBARQ' 'SINV' 'SQ' 'UCP' 'VP' \
        'WHADJP' 'WHADVP' 'WHNP' 'WHPP' 'X')
fi

base=/home/mg1/classes/treebanking
suite_dir=test_suites_v2
for cat in "${cats[@]}"
do
    echo $cat
    $base/supa_docs/sierra.sh \
        -morder $base/supa_docs/macros/ORDER.txt \
        -oporder $base/supa_docs/opfiles/ORDER_TS.txt \
        -treeFile $base/$suite_dir/${cat}/${cat}_PTBtrees_simple.mrg \
        >$base/$suite_dir/${cat}/${cat}_simple.supa
done

rm -f sierra_*
