#!/bin/ksh
#*******************************************************************************************
#  Purpose: Run CTC average for cnv verification 
#       
#    Note: This scripts is specific for ceiling and visibility (cnv). 
#           For ceiling and visibility, in case of claer sky in one member, its forecast
#           will be given a very large value. This very large value may b arbitrary,
#           so it can not be used in the ensemble mean computation of CTC scores
#           (so-called conditional-mean). The better solution to deal with such case  is
#              Step 1. First verify cnv to get CTC stat files for each ensemble members
#              Step 2. Calculate the ensemble mean of CTC among the stat files of all ensemble
#                      members. In other word, get the average of each column
#                      (hit rate, false alarm, correct non, etc) of CTC line type
#              Step 3. Form final CTC stat file for cnv using the averaged CTC columns
#           This script is for step 2 and 3
#
#  Last update: 11/16/2023, by Binbin Zhou Lynker@EMC/NCEP
#   
#******************************************************************************************
set -x 

typeset -Z2 fhr
modnam=$1
fhr=$2

MODEL=`echo $modnam | tr '[a-z]' '[A-Z]'` 
if [ $modnam = gefs ] ; then
   mbrs='01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30'
fi

for vvhour in 00 06 12 18 ; do 

  #***************************************************************************
  # ctc25,ctc26, ctc27 and ctc28 are CTC's No 25, 26, 27 and 27, respectively 
  #*************************************************************************** 	
  for n in 2 3 4 5 6 7 8 9 10 11 12 13 ; do
    ctc25[$n]=0
    ctc26[$n]=0
    ctc27[$n]=0
    ctc28[$n]=0
  done

  #***********************************************
  #Final stst file name for the CTC ensemble mean 
  #***********************************************
  >point_stat_GEFS_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvhour}0000V.stat

   for mbr in $mbrs ; do
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

	if [ $mbr = 30 ] ; then
	  ctc25[$line]=$(( ctc25[$line] / 30 ))
	  ctc26[$line]=$(( ctc26[$line] / 30 ))
	  ctc27[$line]=$(( ctc27[$line] / 30 ))
	  ctc28[$line]=$(( ctc28[$line] / 30 ))
	  data[25]=${ctc25[$line]}
	  data[26]=${ctc26[$line]}
	  data[27]=${ctc27[$line]}
	  data[28]=${ctc28[$line]}
	  if [ $line -eq 1 ] ; then
	      echo  ${data[0]}  ${data[1]}  ${data[2]}  ${data[3]}  ${data[4]}  ${data[5]}  ${data[6]}  ${data[7]}  ${data[8]}  ${data[9]}  ${data[10]}  ${data[11]}  ${data[12]}  ${data[13]}  ${data[14]}  ${data[15]} ${data[16]}  ${data[17]}  ${data[18]}  ${data[19]} ${data[20]}  ${data[21]}  ${data[22]}  ${data[23]}  ${data[24]}  >> point_stat_GEFS_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvhour}0000V.stat
          else
	      echo  ${data[0]}  ${data[1]}  ${data[2]}  ${data[3]}  ${data[4]}  ${data[5]}  ${data[6]}  ${data[7]}  ${data[8]}  ${data[9]}  ${data[10]}  ${data[11]}  ${data[12]}  ${data[13]}  ${data[14]}  ${data[15]} ${data[16]}  ${data[17]}  ${data[18]}  ${data[19]} ${data[20]}  ${data[21]}  ${data[22]}  ${data[23]}  ${data[24]}  ${data[25]}  ${data[26]}  ${data[27]} ${data[28]} 0.5 >> point_stat_GEFS_PREPBUFR_CONUS_FHR${fhr}_CNV_${fhr}0000L_${vday}_${vvhour}0000V.stat
          fi
	fi
       line=$((line+1))
     done < point_stat_${MODEL}_mbr${mbr}_PREPBUFR_CNV_CONUS_FHR_${fhr}0000L_${vday}_${vvhour}0000V.stat

 done

done
