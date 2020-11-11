.PHONY: default
default: packages documentation $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: packages
packages: $(patsubst %.dtx,%.sty,$(wildcard *.dtx))

.PHONY: documentation
documentation: $(patsubst %.dtx,%.pdf,$(wildcard *.dtx))

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

promotion.pdf: promotion.sty | minted
record.pdf: record.sty | minted
statement.pdf: statement.sty | minted
supplements.pdf: supplements.sty | minted record.pdf statement.pdf

include $(shell git rev-parse --show-toplevel)/Makefile.mk
