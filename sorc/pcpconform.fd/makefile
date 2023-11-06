SRCS=pcpconform.f
OBJS=pcpconform.o
CMD=pcpconform
FC=ftn
DEBUG=-check all -ftrapuv
LIBS=${W3EMC_LIB4} ${BACIO_LIB4}
FFLAGS=-FR -cpp -g -traceback
LDFLAGS=
BINDIR=${EXECevs}

$(CMD):		$(OBJS)
	$(FC) $(LDFLAGS) -o $(@) $(OBJS) $(LIBS)
all: $(CMD)
debug:FFLAGS += $(DEBUG)
debug:$(CMD)
clean:
	-rm -f *.o *.lst $(CMD)
install:
	-mv $(CMD) $(BINDIR)/.


