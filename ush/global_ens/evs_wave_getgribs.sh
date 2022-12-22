#!/bin/bash
#
# gets the grib2 files needed for model verification lead times
#

modname=$1

set -x 

if [ ${modname} = 'gefs' ] ; then
  lead_hours="000 003 006 009 012 015 018 021 024 027 030 033 036
              039 042 045 048 051 054 057 060 063 066 069 072 075
              078 081 084 087 090 093 096 099 102 105 108 111 114
              117 120 123 126 129 132 135 138 141 144 147 150 153
              156 159 162 165 168 171 174 177 180 183 186 189 192
              195 198 201 204 207 210 213 216 219 222 225 228 231
              234 237 240 246 252 258 264 270
              276 282 288 294 300 306
              312 318 324 330 336 342 348
              354 360 366 372 378 384"
  date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6} ${PDYm7}
             ${PDYm8} ${PDYm9} ${PDYm10} ${PDYm11} ${PDYm12} ${PDYm13} ${PDYm14}
             ${PDYm15} ${PDYm16} ${PDYm17}"
  cycles="00 06 12 18"
elif [ ${modname} = 'gfs' ] ; then
  lead_hours="000 003 006 009 012 015 018 021 024 027 030 033 036
              039 042 045 048 051 054 057 060 063 066 069 072 075
              078 081 084 087 090 093 096 099 102 105 108 111 114
              117 120 123 126 129 132 135 138 141 144 147 150 153
              156 159 162 165 168 171 174 177 180 183 186 189 192
              195 198 201 204 207 210 213 216 219 222 225 228 231
              234 237 240 243 246 249 252 255 258 261 264 267 270
              273 276 279 282 285 288 291 294 297 300 303 306 309
              312 315 318 321 324 327 330 333 336 339 342 345 348
              351 354 357 360 363 366 369 372 375 378 381 384"
  date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6} ${PDYm7}
             ${PDYm8} ${PDYm9} ${PDYm10} ${PDYm11} ${PDYm12} ${PDYm13} ${PDYm14}
             ${PDYm15} ${PDYm16} ${PDYm17}"
  cycles="00 06 12 18"
elif [ ${modname} = 'nwps' ] ; then
  lead_hours="000 024 048 072 096 120 144"
  date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6}"
  cycles="00 06 12 18"
  # not all cycles may be there!
elif [ ${modname} = 'nfcens' ] ; then
  lead_hours="000 003 006 009 012 015 018 021 024 027 030 033 036
              039 042 045 048 051 054 057 060 063 066 069 072 075
              078 081 084 087 090 093 096 099 102 105 108 111 114
              117 120 123 126 129 132 135 138 141 144 147 150 153
              156 159 162 165 168 171 174 177 180 183 186 189 192
              195 198 201 204 207 210 213 216 219 222 225 228 231
              234 237 240"
  date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6} ${PDYm7}
               ${PDYm8} ${PDYm9} ${PDYm10}"
  cycles="00 12"
elif [ ${modname} = 'glwu' ] ; then 
  # glwu.grlr_500m files from t00z to t23z each have 48 hrs of fcsts.
  # glwu.grlc_2p5km files for 01,07,13,19z each have 149 hrs of fcsts.
  lead_hours="000 001 002 003 004 005 006 007 008 009 010 011 012
              013 014 015 016 017 018 019 020 021 022 023"
  # should be hourly out to day 6, but first have to figure out how
  # to do hourly validation given their output files
  date_list="${PDYm1} ${PDYm2} ${PDYm3} ${PDYm4} ${PDYm5} ${PDYm6}"
  cycles="01 07 13 19"
fi

for theDate in ${date_list} ; do
  
  for cyc in ${cycles} ; do
  
    mkdir -p ${DATA}/${modname}.${theDate}/${cyc}/gridded

    if [ ${modname} = 'nwps' ] || [ ${modname} = 'glwu' ] || [ ${modname} = 'nfcens' ] ; then
      case ${modname} in
        'nwps')
          filename="wmo/grib2.${cyc}.awipsnwps_${region}_CG1"
          ;;
        'glwu')
          filename="glwu.grlc_2p5km.t${cyc}z.grib2"
          ;;
        'nfcens')
          filename="HTSGW_mean.t${cyc}z.grib2"
          ;;
      esac
      cpreq ${COMINmodel}/${modname}.${theDate}/${filename} ${DATA}/${modname}.${theDate}/${cyc}/gridded/.
    fi
    
    if [ ${modname} = 'gefs' ] || [ ${modname} = 'gfs' ] ; then
      for hr in ${lead_hours} ; do
        case ${modname} in
          'gefs')
            filename="gefs.wave.t${cyc}z.mean.global.0p25.f${hr}.grib2"
            ;;
          'gfs')
            filename="gfswave.t${cyc}z.mean.global.0p25.f${hr}.grib2"
            ;;
        esac
        cpreq ${COMINmodel}/${modname}.${theDate}/${cyc}/wave/gridded/${filename} ${DATA}/${modname}.${theDate}/${cyc}/gridded/.
      done  ## hrs loop
    fi
    
    #########################################
    # regular error check per day and cycle  
    #########################################
    nc=`ls ${DATA}/${modname}.${theDate}/${cyc}/gridded/*grib2 | wc -l | awk '{print $1}'`
    echo " Found ${nc} ${DATA}/${modname}.${theDate}/${cyc}/gridded/*grib2 files"
    if [ "${nc}" != '0' ]
    then
      set +x
      echo "Successfully copied the GEFS-Wave grib2 files for ${theDate}"
      [[ "$LOUD" = YES ]] && set -x
    else
      set +x
      echo ' '
      echo '**************************************** '
      echo '*** ERROR : NO GEFS-Wave grib2 FILES *** '
      echo "      for ${modname}.${theDate}/${cyc} "
      echo '**************************************** '
      echo ' '
      echo "${modname}_${RUN} ${theDate} ${cyc} : GEFS-Wave grib2 files missing."
      [[ "$LOUD" = YES ]] && set -x
      ./postmsg "$jlogfile" "FATAL ERROR : NO GEFS-Wave GRIB2 FILES for ${theDate} ${cyc}"
      err_exit "FATAL ERROR: Did not copy the GEFS-Wave grib2 files for ${theDate} ${cyc}"
    fi

  done ## cycle loop

done # theDates loop
