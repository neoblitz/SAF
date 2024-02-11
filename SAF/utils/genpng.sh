#!/bin/bash

dir=$1
if [ "$dir" == "" ]; then
    echo "Specify an input directory or filename to process"
    exit 2
fi

echo "Input directory $dir"
for log in `ls $dir`; do
    if [[ "$log" == *p_*.prof ]]; then
        echo "Processing $log"  
        file=$log
        if [ ! -e $file ]; then
            file=$dir/$log
        fi
        python utils/dev/gprof2dot.py -f pstats $file | dot -Tpng -o $file.png        
    fi
done 