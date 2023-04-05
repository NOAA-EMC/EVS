FOPTS=-O2 -convert big_endian -traceback -mkl -free
FC=ifort
BINDIR= ../exec
LIBS=-L${LIBDIRW3EMC} -l${W3EMCLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
#LIBS=-L${LIBDIRW3NCO} -l${W3NCOLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
SRCS=	jma_merge.f 
CMD=jma_merge
$(CMD): $(SRCS)
	 $(FC) $(FOPTS) $(SRCS) $(LIBS) -o $(CMD)
install:
	-mv $(CMD) ../../exec/.
