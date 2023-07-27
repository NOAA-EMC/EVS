#!/bin/bash
FC=   ftn -convert big_endian    
INC= ${G2_INC4}
BINDIR=../../exec
#mkdir -p $BINDIR
LIBS= ${IP_LIB4} ${W3NCO_LIB4} ${W3EMC_LIB4} ${BACIO_LIB4}  ${SP_LIB4} ${G2_LIB4} ${JASPER_LIB} ${PNG_LIB} ${Z_LIB}
FFLAGS = -O3 -auto -I $(INC)
precip: clean sref_precip.x install
sref_precip.x:
	$(FC) $(FFLAGS) -o $(@) prepare_precip.f $(LIBS)
clean:
	-rm -f sref_precip.x *.o
install:
	-mv sref_precip.x  ${BINDIR}
#
