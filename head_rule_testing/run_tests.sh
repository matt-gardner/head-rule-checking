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
results_file=results.tsv
if [ -e $results_file ]
then
    prompt="Results file $results_file already exists. Press enter to"
    prompt="$prompt overwrite it, and Ctr-C to quit: "
    read -p "$prompt"
    rm -f $results_file
fi
rm -f sierra_*
echo -n "category	num_patterns	num_annotated	" >>$results_file
echo -n "%_annotated	num_correct	%_correct" >>$results_file
echo -n "tok_count	tok_annotated	%_tok_annotated" >>$results_file
echo "tok_correct	%_tok_correct" >>$results_file
for cat in "${cats[@]}"
do
    echo $cat
    $base/input_files/supa_docs/sierra.sh \
        -morder $base/input_files/supa_docs/macros/ORDER.txt \
        -oporder $base/input_files/supa_docs/opfiles/ORDER_TS.txt \
        -treeFile $base/input_files/${cat}/${cat}_PTBtrees.mrg \
        -nosupa
    python test_suite.py $base/annotations/${cat}_annotations.tsv $cat
    #rm -f sierra_*
done

