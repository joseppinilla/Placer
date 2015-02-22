#!/bin/bash


echo BACKUP >> ./backup.txt
while read line
do
	echo $line >> ./backup.txt
done < ./results.txt

rm ./results.txt

FILES=./benchmarks/*
for f in $FILES
do
  echo "Placing $f benchmark..."
	python ./placerA2/placerA2.py -i $f
done

total=0

while read line
do
		var=$((var+1))
		total=$((total+$line))
done < ./results.txt

echo $total/$var
echo $((total / var)) >> ./average.txt








