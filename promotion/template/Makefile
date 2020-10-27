SUBDIRS := $(wildcard */.) ../../graded-review/

.PHONY: default
default: packages $(SUBDIRS) \
         $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: packages
packages:
	$(MAKE) -C ../ packages

.PHONY: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@


export TEXINPUTS := ../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/Makefile.mk
