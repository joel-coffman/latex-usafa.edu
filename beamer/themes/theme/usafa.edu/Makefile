.PHONY: all
all: beamerthemeusafa.edu.sty example.pdf beamerthemeusafa.edu.pdf

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

beamerthemeusafa.edu.pdf: beamercolorthemefalcon.sty beamerthemeusafa.edu.sty example.pdf | minted
beamerthemeusafa.edu.sty:

example.pdf: beamerthemeusafa.edu.sty ../../beamerthemeexamplebase.tex

include $(shell git rev-parse --show-toplevel)/Makefile.mk
