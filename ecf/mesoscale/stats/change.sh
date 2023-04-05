#!/bin/bash


files=`ls *.ecf`

for file in $files ; do
  sed -e "s!EVS-DEV!VERF-DEV!g" $file  > a
  mv a $file
done

