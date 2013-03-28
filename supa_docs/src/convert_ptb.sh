#!/bin/bash

VERSION="0.1"

SCRIPT_DIR="$(dirname "$0")"
ROOT="$SCRIPT_DIR/.."
DATA_DIR="/Users/mdeeringer/ccls/SUPA/data/treebanks/LDC99T42/wsj"
OUT_ROOT="$ROOT/test_results/ptb_v$VERSION"
EXT_OLD="mrg"
EXT_NEW="supa"

mkdir -p "$OUT_ROOT"
while [[ -n "$1" ]]; do
    dir="$1"; shift
    fulldir="$DATA_DIR/$dir"
    if [[ -e "$fulldir" && ! -d "$fulldir" ]]; then
        echo "$fulldir is not a directory, skipping"
        continue
    fi

    mkdir -p "$OUT_ROOT/$dir"
    for file in $(ls "$fulldir"); do
        fullfile="$fulldir/$file"
        if [[ ! -f "$fullfile" ]]; then
            echo "$fullfile is not a regular file, skipping"
            continue
        elif [[ "$file" != *"$EXT_OLD" ]]; then
            echo "$file does not have extension $EXT_OLD, skipping"
            continue
        fi

        outfile="$OUT_ROOT/$dir/$(basename "$file" $EXT_OLD)$EXT_NEW"
        cmd="$ROOT/sierra.sh -treeFile $fullfile > $outfile"
        eval "$cmd"
    done
done
