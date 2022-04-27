SHELL=		/bin/sh

LIBS=           ${W3NCO_LIB4} ${W3EMC_LIB4} ${BACIO_LIB4}
FC=             ifort
FFLAGS=         -FR -cpp 

LDFLAGS=
SRCS=		diffpcp.f
CMD=		diffpcp

all:		$(CMD)

$(CMD): $(SRCS)
	$(FC) $(FFLAGS) $(SRCS) $(LIBS) -o $(CMD)

clean:
	-rm -f *.o *.lst $(CMD)
install:
	-mv $(CMD) ../../exec/.


