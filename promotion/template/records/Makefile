documents := $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: all
all: $(documents)


export TEXINPUTS := ../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex
