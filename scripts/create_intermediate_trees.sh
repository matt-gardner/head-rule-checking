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
suites_dir=test_suites_v2
rm -f sierra_*
for cat in "${cats[@]}"
do
    echo $cat
    $base/supa_docs/sierra.sh \
        -morder $base/supa_docs/macros/ORDER.txt \
        -oporder $base/supa_docs/opfiles/ORDER_TS.txt \
        -treeFile $base/$suites_dir/${cat}/${cat}_PTBtrees_simple.mrg \
        -nosupa
    python create_intermediate.py $cat $suites_dir
    rm -f sierra_*
done

