for cat in 'ADJP' 'ADVP' 'CONJP' 'FRAG' 'INTJ' 'LST' 'NAC' 'NP' 'NX' 'PP' 'PRN' 'PRT' 'QP' 'RRC' 'S' 'SBAR' 'SBARQ' 'SINV' 'SQ' 'UCP' 'VP' 'WHADJP' 'WHADVP' 'WHNP' 'WHPP' 'X'
do
    echo $cat
    input_files/supa_docs/sierra.sh \
        -morder input_files/supa_docs/macros/ORDER.txt \
        -oporder input_files/supa_docs/opfiles/ORDER_TS.txt \
        -treeFile input_files/${cat}/${cat}_PTBtrees_simple.mrg \
        >input_files/${cat}/${cat}_simple.supa
done

rm -f sierra_*
