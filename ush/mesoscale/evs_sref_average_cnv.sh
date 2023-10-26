#!/bin/ksh

set -x 

#vday=20221018

typeset -Z2 fhr
fhr=$1


for vvfhr in 00 06 12 18 ; do 
#for vvfhr in 00  ; do 

  for n in 2 3 4 5 6 7 8 9 10 11 12 13 ; do
    ctc25[$n]=0
    ctc26[$n]=0
    ctc27[$n]=0
    ctc28[$n]=0
  done

  >point_stat_SREF_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvfhr}0000V.stat

  for base_model in arw nmb ; do 
    for mbr in ctl p1 p2 p3 p4 p5 p6 n1 n2 n3 n4 n5 n6 ; do
      	    line=1
      while read -r LINE; do
        set -A data $LINE
	
        if [ $line -eq 1 ] ; then
	  header=$LINE 
        fi   

	if [ $line -ge 2 ] && [ $line -le 13 ] ; then 
          ctc25[$line]=$(( ctc25[$line] + data[25] ))
          ctc26[$line]=$(( ctc26[$line] + data[26] ))
          ctc27[$line]=$(( ctc27[$line] + data[27] ))
          ctc28[$line]=$(( ctc28[$line] + data[28] ))
	fi

	if [ $base_model = nmb ] && [ $mbr = n6 ] ; then
	  ctc25[$line]=$(( ctc25[$line] / 26 ))
	  ctc26[$line]=$(( ctc26[$line] / 26 ))
	  ctc27[$line]=$(( ctc27[$line] / 26 ))
	  ctc28[$line]=$(( ctc28[$line] / 26 ))
	  data[25]=${ctc25[$line]}
	  data[26]=${ctc26[$line]}
	  data[27]=${ctc27[$line]}
	  data[28]=${ctc28[$line]}
	  if [ $line -eq 1 ] ; then
	      echo  ${data[0]}  ${data[1]}  ${data[2]}  ${data[3]}  ${data[4]}  ${data[5]}  ${data[6]}  ${data[7]}  ${data[8]}  ${data[9]}  ${data[10]}  ${data[11]}  ${data[12]}  ${data[13]}  ${data[14]}  ${data[15]} ${data[16]}  ${data[17]}  ${data[18]}  ${data[19]} ${data[20]}  ${data[21]}  ${data[22]}  ${data[23]}  ${data[24]}  >> point_stat_SREF_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvfhr}0000V.stat
          else
	      echo  ${data[0]}  ${data[1]}  ${data[2]}  ${data[3]}  ${data[4]}  ${data[5]}  ${data[6]}  ${data[7]}  ${data[8]}  ${data[9]}  ${data[10]}  ${data[11]}  ${data[12]}  ${data[13]}  ${data[14]}  ${data[15]} ${data[16]}  ${data[17]}  ${data[18]}  ${data[19]} ${data[20]}  ${data[21]}  ${data[22]}  ${data[23]}  ${data[24]}  ${data[25]}  ${data[26]}  ${data[27]} ${data[28]} 0.5 >> point_stat_SREF_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvfhr}0000V.stat
          fi
	fi
       line=$((line+1))
     done < point_stat_SREF${base_model}_${mbr}_PREPBUFR_CONUS_FHR${fhr}_${fhr}0000L_${vday}_${vvfhr}0000V.stat

  done

 done

done
