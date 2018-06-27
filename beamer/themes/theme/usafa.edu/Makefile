.PHONY: default
default: beamerthemeusafa.edu.sty example.pdf beamerthemeusafa.edu.pdf

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

beamerthemeusafa.edu.pdf: beamerthemeusafa.edu.sty example.pdf | minted

example.pdf: beamerthemeusafa.edu.sty

include ../../../../Makefile.mk
