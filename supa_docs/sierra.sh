#!/bin/bash

# FILE: sierra.sh
# DESCRIPTION: Pipeline for converting phrase structure parse trees to SUPA
#              dependency format.
# AUTHOR: Michael Deeringer (mjd2188@columbia.edu)

# TODO: find way to run over multiple tree files (e.g. check if treeFile is a
#       directory)
# TODO: allow user to specify tree separator type/pattern.

sierra_root="$(dirname "$0")"
src_dir="$sierra_root/src"
tsurgeon="$src_dir/tsurgeon.sh"
indexer="$src_dir/index_words.py"
tree2supa="$src_dir/tree_to_supa.py"

usage() {
    echo "Usage: $0 [options] -treeFile filename"
    echo "       [-pre preamble_opfile]"
    echo "       [-macros macro_file | -morder macro_order_file]"
    echo "       [-oporder op_order_file | opfile1 opfile2 ... |"
    echo "        -po pattern operation]"
    echo "       [-nosupa]"
    exit 1
}

concat_macros() {
    local order_file="$1"
    # The user has provided a macro order file, so we can derive the macro
    # directory path.
    macro_dir="$(dirname "$order_file")"
    macro_file="$2"
    local line
    while read line; do
        line="$macro_dir/$line"
        if [[ -f "$line" ]]; then
            cat "$line" >> "$macro_file"
            echo >> "$macro_file"
        else
            echo "Macro file \"$line\" does not exist!" 1>&2
            exit 1
        fi
    done < "$order_file"
    return 0
}

extend_op_files() {
    local order_file="$1"
    # The user has provided an operation order file, so we can derive the opfile
    # directory path.
    op_dir="$(dirname "$order_file")"
    local line
    while read line; do
        line="$op_dir/$line"
        if [[ -f "$line" ]]; then
            op_files[${#op_files[@]}]="$line"
        else
            echo "Opfile \"$line\" does not exist!" 1>&2
            exit 1
        fi
    done < "$order_file"
    return 0
}

if (( $# < 2 )); then
    echo "Found $# argument(s), need at least 2" 1>&2
    usage
fi

while [[ -n "$1" ]]; do
    case "$1" in
        -pre)
            # Handle preamble operation file.
            shift
            if [[ -e "$1" ]]; then
                pre_op_file="$1"
                shift
            else
                echo "Preamble op file \"$1\" does not exist!" 1>&2
                usage
            fi
            ;;
        -macros)
            # Handle a macro file.
            shift
            if [[ ! -n "$macro_file" && -e "$1" ]]; then
                macro_file="$1"
                shift
            elif [[ -n "$macro_file" ]]; then
                echo "Redundant option -macros; user has already provided macro info" 1>&2
                usage
            else
                echo "Macro file \"$1\" does not exist!" 1>&2
                usage
            fi
            ;;
        -morder)
            # Handle a macro order file.
            shift
            if [[ ! -n "$macro_file" && -e "$1" ]]; then
                outfile="$(mktemp "${TMPDIR}sierra_macros.XXXXXXXX")"
                echo "Generating macro file from macro order file $1: $outfile" 1>&2
                concat_macros "$1" "$outfile"
                shift
            elif [[ -n "$macro_file" ]]; then
                echo "Redundant option -morder; user has already provided macro info" 1>&2
                usage
            else
                echo "Macro order file \"$1\" does not exist!" 1>&2
                usage
            fi
            ;;
        -oporder)
            # Handle an operation order file.
            shift
            if [[ -e "$1" ]]; then
                echo "Including ops from operation order file $1" 1>&2
                extend_op_files "$1"
                shift
            else
                echo "Operation order file \"$1\" does not exist!" 1>&2
                usage
            fi
            ;;
        -treeFile)
            # Handle a tree file.
            shift
            if [[ -e "$1" ]]; then
                tree_file="$1"
                shift
            else
                echo "Tree file \"$1\" does not exist!" 1>&2
                usage
            fi
            ;;
        -po)
            # Handle a pattern-operation pair of strings.
            shift
            if [[ -n "$1" && -n "$2" ]]; then
                pattern="$1"
                operation="$2"
                shift; shift
            else
                echo "Incomplete pattern-operation pair!" 1>&2
                echo "    pattern: $1" 1>&2
                echo "    operation: $2" 1>&2
                usage
            fi
            ;;
        *.op)
            # Append this operation file to the end of op_files.
            op_files[${#op_files[@]}]="$1"
            shift
            ;;
        -m)
            # Ignore Tsurgeon option -m, which prints "before" and "after" trees
            echo "Ignoring option -m" > /dev/tty
            shift
            ;;
        -nosupa)
            # No SUPA for you!
            echo "Just generating post-processed tree, not converting it to SUPA format" > /dev/tty
            shift
            nosupa=true
            ;;
        *)
            # Handle any other arg
            options[${#options[@]}]="$1"
            shift
            ;;
    esac
done

# We need a tree file.
if [[ ! -n "$tree_file" ]]; then
    echo "Must provide a tree file!" 1>&2
    usage
fi

# Determine directories for opfiles and macro files, for use further below.
[[ -n "$op_dir" ]] || op_dir="$sierra_root/opfiles"
[[ -n "$macro_dir" ]] || macro_dir="$sierra_root/macros"

if [[ -n "$op_files" && -n "$pattern" ]]; then
    echo "Cannot have op files and a pattern-operation pair!" 1>&2
    usage
elif [[ ! -n "$op_files" && ! -n "$pattern" ]]; then
    # If there's nothing we can use to determine the op(s) to run, use the
    # default op order file.
    default_order_file="$op_dir/ORDER.txt"
    echo "Using default operation order file $default_order_file" > /dev/tty
    extend_op_files "$default_order_file"
fi

# If no macro file is provided, create and use a default macro file.
if [[ ! -n "$macro_file" ]]; then
    default_order_file="$macro_dir/ORDER.txt"
    outfile="$(mktemp "${TMPDIR}sierra_macros.XXXXXXXX")"
    echo "Generating macro file from default order file $default_order_file: $outfile" > /dev/tty
    concat_macros "$default_order_file" "$outfile"
fi

################
# Run commands #
################

# Run pre-indexing ops.
if [[ ! -n "$pre_op_file" ]]; then
    default_pre_op_file="$op_dir/preIndexing.op"
    echo "Using default preamble operation file $default_pre_op_file" > /dev/tty
    pre_op_file="$default_pre_op_file"
fi

# (The -t option to mktemp caused some incompatability problems, so creating
# a template manually.)
tmpfile="$(mktemp "${TMPDIR}sierra_preindexing.XXXXXXXX")"
echo "Determining which tokens to index -- output to $tmpfile" > /dev/tty
"$tsurgeon" "${options[@]}" -macros "$macro_file" -treeFile "$tree_file" "$pre_op_file" > "$tmpfile"
tree_file="$tmpfile"

# Index the tokens in each tree, by word order.
tmpfile="$(mktemp "${TMPDIR}sierra_indexed.XXXXXXXX")"
echo "Indexing tokens -- output to $tmpfile" > /dev/tty
"$indexer" "$tree_file" > "$tmpfile"
tree_file="$tmpfile"

# Run the Tsurgeon ops.
tmpfile="$(mktemp "${TMPDIR}sierra_postop.XXXXXXXX")"
echo "Running Tsurgeon operations -- output to $tmpfile" > /dev/tty
cmd=( "$tsurgeon" "${options[@]}"
      -macros "$macro_file"
      -treeFile "$tree_file" )
if [[ -n "$op_files" ]]; then
    op_array=( "${op_files[@]}" )
else
    op_array=( "-po" "$pattern" "$operation" )
fi
# Concatenate cmd and op_array.
cmd=( "${cmd[@]}" "${op_array[@]}" )
echo "(Tsurgeon command: ${cmd[@]})" > /dev/tty

# For testing
#exit

eval "${cmd[@]}" > "$tmpfile"

tree_file="$tmpfile"

if [ ! $nosupa ]; then
    # Finally, print out the dependencies in SUPA format.
    echo -e "Printing dependencies in SUPA format\n" > /dev/tty
    "$tree2supa" "$tree_file"
fi

echo -e "Done!\n" > /dev/tty
