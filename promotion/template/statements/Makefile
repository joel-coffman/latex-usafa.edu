documents := $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: default
default: $(documents)


export TEXINPUTS := ../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/Makefile.mk
