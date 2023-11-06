SRCS=ecm_gfs_look_alike_new.f90
CMD=ecm_gfs_look_alike_new
FFLAGS += -O2 -convert big_endian -mkl -free
DEBUG=-check all -ftrapuv
LIBS=-L${LIBDIRW3EMC} -l${W3EMCLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
BINDIR=${EXECevs}

$(CMD): $(SRCS)
	 $(FC) $(FFLAGS) $(SRCS) $(LIBS) -o $(CMD)
all: $(CMD)
debug:FFLAGS += $(DEBUG)
debug:$(CMD)
clean:
	-rm -f *.o $(CMD)
install:
	-mv $(CMD) $(BINDIR)/.
