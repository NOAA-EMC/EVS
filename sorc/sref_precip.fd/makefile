SRCS=sref_precip.f
CMD=sref_precip.x
DEBUG=-check all -ftrapuv
INC= ${G2_INC4}
LIBS= ${IP_LIB4} ${W3EMC_LIB4} ${BACIO_LIB4}  ${SP_LIB4} ${G2_LIB4} ${JASPER_LIB} ${PNG_LIB} ${Z_LIB}
FFLAGS += -O3 -auto -convert big_endian -I $(INC)
BINDIR=${EXECevs}

$(CMD):
	$(FC) $(FFLAGS) -o $(@) $(SRCS) $(LIBS)
all: $(CMD)
debug:FFLAGS += $(DEBUG)
debug:$(CMD)
clean:
	-rm -f *.o $(CMD)
install:
	-mv $(CMD)  $(BINDIR)/.
