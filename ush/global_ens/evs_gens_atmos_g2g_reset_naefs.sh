#!/bin/ksh

#Note: This script is to adjust CMCE members by adding the difference between GFS analysis and CMC analysis to
#each CMCE member.
 
set -x


NDATE=${NDATE:-/gpfs/dell1/nco/ops/nwprod/prod_util.v1.1.0/exec/ips/ndate}


if [ $RUN = atmos ] ; then
  leads='12  24 36 48 60 72 84 96 108 120 132 144 156 168 180 192 204 216 228 240 252 264 276 288 300 312 324 336 348 360 372 384'
  vcycs="00 12" 
else
  leads='24 48 72 96  120 144 168 192 216 240 264 288 312 336 360 384'
  vcycs="00"
fi  

mkdir -p $WORK/naefs

 cd $WORK/naefs

for vcyc in $vcycs ; do 
 
   ln -sf ${COMIN}.${vday}/gefs/gfsanl.t${vcyc}z.grid3.f000.grib2 gfsanl
   ln -sf ${COMIN}.${vday}/cmce/cmcanl.t${vcyc}z.grid3.f000.grib2 cmcanl


 for lead in $leads ; do
   obsv_cyc=${vday}${vcyc}     #validation time: xxxx.tvcycz.f00
   fcst_time=`$NDATE -$lead $obsv_cyc`
   fyyyymmdd=${fcst_time:0:8}
   fcyc=${fcst_time:8:2}
  
   fhr=$lead
   typeset -Z3 fhr

   if [ $gefs_number = 20 ] ; then
    mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20"
   elif [ $gefs_number = 30 ] ; then
    mbrs="01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30"
   fi

   for mbr in $mbrs ; do
    if [ $RUN = headline ] ; then
      #Note: in headline.yyyymmdd/gefs, the files were from atmos.yyyymmdd/gefs_bc 
      ln -sf  ${COMIN}.${fyyyymmdd}/gefs/gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
    else 
      ln -sf  ${COMIN}.${fyyyymmdd}/gefs_bc/gefs_bc.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
    fi  
   done

   for mbr in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 ; do
    if [ $RUN = headline ] ; then
     #Note: in headline.yyyymmdd/cmce, the files were from atmos.yyyymmdd/cmce_bc 
     ln -sf  ${COMIN}.${fyyyymmdd}/cmce/cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
    else
     ln -sf  ${COMIN}.${fyyyymmdd}/cmce_bc/cmce_bc.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2  cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2
    fi
   done

   if [ $gefs_number = 20 ] ; then
     sed -e "s!CYC!$fcyc!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_gefs_file_list.20 > gefs_file_list.t${fcyc}z.f${fhr}
   elif [  $gefs_number = 30 ] ; then      
     sed -e "s!CYC!$fcyc!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_gefs_file_list.30 > gefs_file_list.t${fcyc}z.f${fhr}
   fi 

   sed -e "s!CYC!$fcyc!g" -e "s!GRID!3!g" -e "s!FHR!$fhr!g" $ENS_LIST/evs_g2g_cmce_file_list > cmce_file_list.t${fcyc}z.f${fhr}

   echo "gefs_file_list.t${fcyc}z.f${fhr}  cmce_file_list.t${fcyc}z.f${fhr}"|$EXECevs/evs_g2g_adjustCMC.x

   for mb in $mbrs ; do
     mbr=$mb
     typeset -Z2 mbr
     mv gefs.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2     naefs.ens${mbr}.${fyyyymmdd}.t${fcyc}z.grid3.f${fhr}.grib2
   done
  
   for mb in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 ; do
     mbr=$mb
     typeset -Z2 mbr
     if [ $gefs_number = 20 ] ; then
	mbr50=$((mb+20))
     elif [ $gefs_number = 30 ] ; then
        mbr50=$((mb+30))
     fi 

     if [ -s cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2.adj ] ; then
      mv cmce.ens${mbr}.t${fcyc}z.grid3.f${fhr}.grib2.adj naefs.ens${mbr50}.${fyyyymmdd}.t${fcyc}z.grid3.f${fhr}.grib2
     fi 
   done


 done
done

cd $WORK


