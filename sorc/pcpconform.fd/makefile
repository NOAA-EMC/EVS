SRCS=pcpconform.f
OBJS=pcpconform.o
CMD=pcpconform
FC=ifort
DEBUG=-check all -ftrapuv
LIBS=${W3NCO_LIB4} ${W3EMC_LIB4} ${BACIO_LIB4}
FFLAGS=-FR -cpp 
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


