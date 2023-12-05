SRCS=ukm_hires_merge.f90
CMD=ukm_hires_merge
FFLAGS += -O2 -convert big_endian -mkl
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
