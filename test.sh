#!/bin/bash


echo BACKUP >> ./backup.txt
while read line
do
	echo $line >> ./backup.txt
done < ./results.txt

rm ./results.txt

FILES=./benchmarks/*

for py in "placerA2b.py" "placerA2c.py" "placerA2d.py" "placerA2.py"
do
	for s in 1 32 64 85
	do
		for t in 1 10 100
		do
				for f in $FILES
				do
					echo "Placing $f benchmark..."
					time python ./placerA2/$py -q -t $t -s $s -i $f
				done

				total=0

				while read line
				do
						var=$((var+1))
						total=$((total+$line))
				done < ./results.txt

				echo $total/$var
				echo $((total / var)) >> ./average.txt
		done #Temp
	done #Seed
done #Python
