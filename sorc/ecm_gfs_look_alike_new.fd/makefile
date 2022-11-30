FOPTS=-O2 -convert big_endian -traceback -mkl -free
FC=ifort
BINDIR= ../exec
LIBS=-L${LIBDIRW3EMC} -l${W3EMCLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
#LIBS=-L${LIBDIRW3NCO} -l${W3NCOLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
SRCS=	ecm_gfs_look_alike_new.f90 
CMD=ecm_gfs_look_alike_new
$(CMD): $(SRCS)
	 $(FC) $(FOPTS) $(SRCS) $(LIBS) -o $(CMD)
install:
	-mv $(CMD) ../../exec/.
