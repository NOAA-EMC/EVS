set -x

mkdir -p $DATA/modelinput
cd $DATA/modelinput

mkdir -p $COMOUT/${RUN}.${VDATE}/${MODELNAME}

for hour in 06 12
do

for biastyp in raw bc
do

export biastyp
echo $biastyp

if [ $biastyp = "raw" ]
then
export bctag=
fi

if [ $biastyp = "bc" ]
then
export bctag=_bc
fi


if [ $hour -eq 06 ]
then
wgrib2 -d 1 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "6-29 hour ave fcst"  -grib out1.grb2
wgrib2 -d 2 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "30-53 hour ave fcst" -grib out2.grb2
wgrib2 -d 3 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "54-77 hour ave fcst" -grib out3.grb2
cat out1.grb2 out2.grb2 out3.grb2 > $COMOUT/${RUN}.${VDATE}/${MODELNAME}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2
fi

if [ $hour -eq 12 ]
then
wgrib2 -d 1 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "0-23 hour ave fcst" -grib out1.grb2
wgrib2 -d 2 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "24-47 hour ave fcst" -grib out2.grb2
wgrib2 -d 3 $COMINaqm/cs.${VDATE}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2 -set_ftime "48-71 hour ave fcst" -grib out3.grb2
cat out1.grb2 out2.grb2 out3.grb2 > $COMOUT/${RUN}.${VDATE}/${MODELNAME}/aqm.t${hour}z.max_8hr_o3${bctag}.148.grib2
fi

done
done

exit

