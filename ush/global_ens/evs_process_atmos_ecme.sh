#####################################################################
#
# 2015-06-12: Modified from Yan.Luo's script
#
set +x
#####################################################################

dcom=${DCOMIN} 
cd $WORK

#####################################################################
# Set names of executable utilities
#####################################################################

getvhour=$NHOUR
ndate=$NDATE
cnvgrib=$CNVGRIB

#########################################################
# !!! DEFINE MAXIMUM NUMBER OF PERTURBATION RECORDS
# (This number does NOT include the LRC or HRC)
#########################################################


CDATE=$1  #day+running cycle
cyc=$2

#CDATE=2021080200
#cyc=00
cycle=t${cyc}z


#####################################################################
# Set date variables to process CDATE data  
#
#####################################################################

#Binbin tdate=`$ndate -24 $CDATE | cut -c1-8`
tdate=`$ndate 0 $CDATE | cut -c1-8`              #Binbin set tdate = CDATE 

cent=`echo $tdate | cut -c1-2 `
yy=`  echo $tdate | cut -c3-4 `
mm=`  echo $tdate | cut -c5-6 `
dd=`  echo $tdate | cut -c7-8 `

indate=$cent$yy$mm$dd

cent=`echo $indate | cut -c1-2 `
yy=`  echo $indate | cut -c3-4 `
mm=`  echo $indate | cut -c5-6 `
dd=`  echo $indate | cut -c7-8 `

yyyymmdd=$indate
yyyymmddhh=${yyyymmdd}${cyc}
ymdh=${indate}${cyc}
imdh=${mm}${dd}${cyc}
hh=${cyc}
echo " Date to copy is $indate"
yymmddhh=${yy}${mm}${dd}${hh}

get_ecme='yes'

if [ $get_ecme = 'yes' ] ; then

VAR[1]=':10U:'
VAR[2]=':10V:'
VAR[3]=':U:kpds5=131:kpds6=100:kpds7=850:'
VAR[4]=':V:kpds5=132:kpds6=100:kpds7=850:'
VAR[5]=':U:kpds5=131:kpds6=100:kpds7=250:'
VAR[6]=':V:kpds5=132:kpds6=100:kpds7=250:'
VAR[7]=':GH:kpds5=156:kpds6=100:kpds7=500:'
VAR[8]=':GH:kpds5=156:kpds6=100:kpds7=700:'
VAR[9]=':GH:kpds5=156:kpds6=100:kpds7=1000:'
VAR[10]=':T:kpds5=130:kpds6=100:kpds7=500:'
VAR[11]=':T:kpds5=130:kpds6=100:kpds7=850:'
VAR[12]=':2T:'
VAR[13]=':TCC:'
VAR[14]=':MSL:'
VAR[15]=':2D:'
VAR[20]=':TP:'
VAR[21]=':SF:'

hourix=0
#while [ ${hourix} -lt 61 ]; do
while [ ${hourix} -lt 31 ]; do
  let hourinc=hourix*12
  #let hourinc=hourix*6
  vymdh=` ${ndate} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${getvhour} ${vymdh} ${ymdh}`

  if [ ${hourix} = 0 ] ; then
    DCD=${dcom}/$yyyymmdd/wgrbbul/ecmwf/DCD${imdh}00${vmdh}001

    if [ -s $DCD ] ; then
      >$outdata/ecmanl.t${cyc}z.grid3.f000.grib1
      for n in 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 ; do
       $WGRIB $DCD|grep "${VAR[$n]}"|$WGRIB -i -grib $DCD -o x 
       cat x >> $outdata/ecmanl.t${cyc}z.grid3.f000.grib1
      done
     else
        export subject="ECME Data Missing for EVS ${COMPONENT}"
        echo "Warning:  No ECME data for ${ymdh}" > mailmsg
        echo Missing files are in ${dcom}/$yyyymmdd/wgrbbul/ecmwf  >> mailmsg
        echo "Job ID: $jobid" >> mailmsg
        cat mailmsg | mail -s "$subject" $maillist
     fi 
  fi 

  E1E=${dcom}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001

  >E1E.${hourinc} 
  for n in 1 2 12 13 14 15 ; do
     $WGRIB $E1E|grep "${VAR[$n]}"|$WGRIB -i -grib $E1E -o x 
     cat x >> E1E.${hourinc}
  done
 
  h3=${hourinc}
  typeset -Z3 h3
  mbr=1
   while [ ${mbr} -le 50 ]; do
    m2=$mbr
    typeset -Z2 m2
     
    $WGRIB E1E.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E.${hourinc} -o $outdata/ecme.ens${m2}.t${cyc}z.grid4.f${h3}.grib1
    mbr=$((mbr+1))
   
   done
   rm E1E.${hourinc}
   

  let hourix=hourix+1

done 


hourix=0
while [ ${hourix} -lt 31 ]; do

  let hourinc=hourix*12
  vymdh=` ${ndate} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${getvhour} ${vymdh} ${ymdh}`

  E1E=${dcom}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001

  >E1E_apcp.${hourinc}
  for n in 20 21 ; do
     $WGRIB $E1E|grep "${VAR[$n]}"|$WGRIB -i -grib $E1E -o x
     cat x >> E1E_apcp.${hourinc}
  done

  h3=${hourinc}
  typeset -Z3 h3
  mbr=1
   while [ ${mbr} -le 50 ]; do
    m2=$mbr
    typeset -Z2 m2

    $WGRIB E1E_apcp.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E_apcp.${hourinc} -o $outdata/ecme.ens${m2}.t${cyc}z.grid4_apcp.f${h3}.grib1
    mbr=$((mbr+1))

   done
   rm E1E_apcp.${hourinc}

  let hourix=hourix+1

done

fi 

VAR[1]=':U:kpds5=131:kpds6=100'
VAR[2]=':V:kpds5=132:kpds6=100'
VAR[3]=':GH:kpds5=156:kpds6=100'
VAR[4]=':T:kpds5=130:kpds6=100'
VAR[5]=':R:kpds5=157:kpds6=100'

hourix=0
while [ ${hourix} -lt 31 ]; do

  let hourinc=hourix*12
  #let hourinc=hourix*6
  vymdh=` ${ndate} ${hourinc} ${ymdh}`
  vmdh=`  echo ${vymdh} | cut -c5-10`
  vhour=` ${getvhour} ${vymdh} ${ymdh}`

  E1E=${dcom}/$yyyymmdd/wgrbbul/ecmwf/E1E${imdh}00${vmdh}001
  
 >E1E_vertical.${hourinc}

  for n in 1 2 3 4 5  ; do
 
   for level in 50 100 200 300 400 500 700 850 925 1000 ; do 
     $WGRIB $E1E|grep "${VAR[$n]}:kpds7=${level}:"|$WGRIB -i -grib $E1E -o x
     cat x >> E1E_vertical.${hourinc}
   done
 
  done

  h3=${hourinc}
  typeset -Z3 h3
  mbr=1
   while [ ${mbr} -le 50 ]; do
    m2=$mbr
    typeset -Z2 m2

    $WGRIB E1E_vertical.${hourinc}|grep "forecast $mbr:"|$WGRIB -i -grib E1E_vertical.${hourinc} -o E1E_vertical.${hourinc}.mbr${mbr}
    cat E1E_vertical.${hourinc}.mbr${mbr} >> $outdata/ecme.ens${m2}.t${cyc}z.grid4.f${h3}.grib1

    mbr=$((mbr+1))

   done
   rm E1E_vertical.${hourinc}*
   rm E1E_vertical.${hourinc}*


  let hourix=hourix+1

done

