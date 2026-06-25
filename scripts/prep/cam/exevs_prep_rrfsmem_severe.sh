#!/bin/bash
###############################################################################
# Name of Script: exevs_prep_rrfsmem_severe.sh
# Contact(s):     Marcel G. Caron (marcel.caron@noaa.gov)
# Purpose of Script: This script preprocesses RRFS Member UH data for 
#                    CAM severe verification.
###############################################################################


set -x

echo 
echo " ENTERING SUB SCRIPT $0 "
echo

set -x


############################################################
# Define surrogate severe settings
############################################################

export machine=${machine:-"WCOSS2"}
export VERIF_GRID=G211
export VERIF_GRID_DX=81.271
export GAUSS_RAD=120


############################################################
# Set some model-specific environment variables 
############################################################

export MODEL_INPUT_DIR=${COMINrrfs}

export MXUPHL25_THRESH1=75.0


if [ $vhr -eq 00 ];then
   nloop=2
   fhr_beg1=12
   fhr_end1=36
   fhr_beg2=36
   fhr_end2=60

elif [ $vhr -eq 06 ]; then
   nloop=2
   fhr_beg1=6
   fhr_end1=30
   fhr_beg2=30
   fhr_end2=54

elif [ $vhr -eq 12 ]; then
   nloop=2
   fhr_beg1=0
   fhr_end1=24
   fhr_beg2=24
   fhr_end2=48

elif [ $vhr -eq 18 ]; then
   nloop=1
   fhr_beg1=18
   fhr_end1=42

else
   err_exit "The given vhr \"${vhr}\" is unsupported"

fi

export nloop
export fhr_beg1
export fhr_end1
export fhr_beg2
export fhr_end2

############################################################
# Write poescript for each domain and use case
############################################################

njob=0

# Create output directory for GridStat (and EnsembleStat) runs
mkdir -p $DATA/gen_ens_prod
mkdir -p $DATA/pcp_combine
mkdir -p $DATA/sspf

MEMNUM="${mem}"
echo "${USHevs}/${COMPONENT}/evs_rrfs_severe_prep.sh $MEMNUM $njob" >> $DATA/poescript
njob=$((njob+1))


###################################################################
# Run the command file
###################################################################

chmod 775 $DATA/poescript

export MP_PGMMODEL=mpmd
export MP_CMDFILE=${DATA}/poescript

if [ "$USE_CFP" = "YES" ]; then

   echo "running cfp"
   mpiexec -np $nproc --cpu-bind verbose,core cfp ${MP_CMDFILE}
   export err=$?; err_chk
   echo "done running cfp"

else

   echo "not running cfp"
   ${MP_CMDFILE}
   export err=$?; err_chk

fi


###################################################################
# Copy hourly output to $COMOUT
###################################################################

# Copy final output to $COMOUT
if [ $SENDCOM = YES ]; then
 mkdir -p $COMOUT/${RUN}.${INITDATE}/${modsys}
 for FILE in $DATA/pcp_combine/${modsys}.${INITDATE}/*; do
    if [ -s "$FILE" ]; then
       cp -v $FILE $COMOUT/${RUN}.${INITDATE}/${modsys}/.
    fi
 done
 for FILE in $DATA/sspf/${modsys}.${INITDATE}/*; do
    if [ -s "$FILE" ]; then
       cp -v $FILE $COMOUT/${RUN}.${INITDATE}/${modsys}/.
    fi
 done
fi
