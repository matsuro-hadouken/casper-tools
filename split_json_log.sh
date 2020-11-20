#!/bin/bash

# Split huge JSON logs in to small parts.
# Original source: https://stackoverflow.com/a/56101625 by 'luvzfootball'

if [ $# -ne 2 ]
then
    echo "usage: $0 file_to_split.json nb_bytes_max_per_split"
    exit 1
fi
if [[ -r $1 ]]
then
    input=$1
    echo "reading from file '$input'"
else
    echo "cannot read from specified input file '$1'"
    exit 2
fi
if [[ $2 = *[[:digit:]]* ]]; then
    maxbytes=$2
    echo "taking maximum bytes '$maxbytes'"
else
    echo "provided maximum number of bytes '$2' is not numeric"
    exit 3
fi

start=0
over=0
iteration=0
inputsize=`cat $input|wc -c`
tailwindow="$input.tail"
echo "input file size: $inputsize"
tmp="$input.tmp"
cp $input $tmp
sed -e ':a' -e 'N' -e '$!ba' -e 's/}[[:space:]]*,[[:space:]]*{/},{/g' -i'.back' $tmp
rm "$tmp.back"
inputsize=`cat $tmp|wc -c`
if [ $inputsize -eq 0 ]; then
    cp $input $tmp
    sed -e 's/}[[:space:]]*,[[:space:]]*{/},{/g' -i'.back' $tmp
    rm "$tmp.back"
fi
inputsize=`cat $tmp|wc -c`
while [ $over -eq 0 ]; do
    output="$input.$iteration"
    if [ $iteration -ne 0 ]; then
                echo -n "[{">$output
    else
                echo -n "">$output
    fi
    tailwindowsize=`expr $inputsize - $start`
    cat $tmp|tail -c $tailwindowsize>$tailwindow
    tailwindowresultsize=`cat $tailwindow|wc -c`
    if [ $tailwindowresultsize -le $maxbytes ]; then
        cat $tailwindow>>$output
        over=1
    else
        cat $tailwindow|head -c $maxbytes|sed -E 's/(.*)\},\{(.*)/\1}]/'>>$output
    fi
    jsize=`cat $output|wc -c`
    start=`expr $start + $jsize`
    if [ $iteration -eq 0 ]; then
        start=`expr $start + 1`
    else
        start=`expr $start - 1`
    fi
    endofj=`cat $output|tail -c 3`
    if [ $over -ne 1 ]; then
        if [ ${endofj:1:2} != "}]" ]; then
            if [ ${endofj:0:2} != "}]" ]; then
                echo -e "ERROR: at least one split pattern wasn't found. Aborting. This could be due to wrongly formatted json or due to a json entry too long compared to the provided maximum bytes. Maybe you should try increasing this parameter?\a"
                exit 4
            fi
        fi
    fi
    jsizefinal=`cat $output|wc -c`
    echo "wrote $jsizefinal bytes of json for iteration $iteration to $output"
    iteration=`expr $iteration + 1`
done
rm $tailwindow
rm $tmp
