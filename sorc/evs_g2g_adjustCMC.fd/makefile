#!/bin/sh
#
#  This makefile is to compile ensembel production generator
#  Author: Binbin Zhou
#  OS: Intel WCOSS2
#

FC=     ftn -convert big_endian
INC= ${G2_INC4}
BINDIR= ../../exec
LIBS= ${IP_LIB4} ${W3NCO_LIB4} ${W3EMC_LIB4} ${BACIO_LIB4}  ${SP_LIB4} ${G2_LIB4} ${JASPER_LIB} ${PNG_LIB} ${Z_LIB}
FFLAGS = -O3 -auto -I $(INC)
CMCE= evs_g2g_adjustCMC.x

cmce:	cleanCMCE $(CMCE) installCMCE
$(CMCE):
	$(FC) $(FFLAGS) -o $(@)  evs_g2g_adjustCMC.f $(LIBS)
cleanCMCE:
	-rm -f *.o $(CMCE)
installCMCE:
	-mv $(CMCE) ${BINDIR}/
#
