.PHONY: default
default: packages $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: packages
packages:
	$(MAKE) -C ../../ packages


export TEXINPUTS := ../../:../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/Makefile.mk
