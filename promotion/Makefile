.PHONY: default
default: $(patsubst %.dtx,%.sty,$(wildcard *.dtx)) \
         $(patsubst %.dtx,%.pdf,$(wildcard *.dtx))

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

promotion.pdf: promotion.sty | minted
record.pdf: record.sty | minted
statement.pdf: statement.sty | minted

include $(shell git rev-parse --show-toplevel)/Makefile.mk
