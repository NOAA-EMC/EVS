#!/bin/ksh
#*********************************************************************
# Purpose: Calculation of the day when ACC drops below 0.6
# 
#  Log history: 
#               01/17/2024: Created by Binbin Zhou, Lynker/EMC
#********************************************************************
echo "Days:  ACC for $model" >> $output
i=1
while [ $i -le 16 ] ; do
  read LINE 
  acc[$i]=$LINE
  echo "   $i: ${acc[$i]}" >> $output
  i=$((i+1))
done

i=1
while [ $i -le 15 ] ; do
  j=$((i+1))
  if [ ${acc[$i]} -gt 0.6 ] && [ ${acc[$j]} -lt 0.6 ] ; then
    loc=$i 
  fi
  i=$((i+1))
done

acc1=${acc[$loc]}
loc_1=$((loc+1))

acc2=${acc[$loc_1]}


a=$((acc1-0.6))
b=$((0.6-acc2))
c=$((a+b))
d=$((a/c))
day=$((loc+d))

DAY=`printf '%.4f' $day`
echo The day when ACC drops below 0.6 for $model is:  $DAY >> $output 

