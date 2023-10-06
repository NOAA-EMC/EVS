SRCS=ukm_hires_merge.f
CMD=ukm_hires_merge
FC=ifort
FOPTS=-O2 -convert big_endian -traceback -mkl -free
DEBUG=-check all -ftrapuv
LIBS=-L${LIBDIRW3EMC} -l${W3EMCLIB} -L${LIBDIRBACIO} -l${BACIOLIB}
BINDIR=${EXECevs}

$(CMD): $(SRCS)
	 $(FC) $(FOPTS) $(SRCS) $(LIBS) -o $(CMD)
all: $(CMD)
debug:FOPTS += $(DEBUG)
debug:$(CMD)
clean:
	-rm -f $(CMD)
install:
	-mv $(CMD) $(BINDIR)/.
