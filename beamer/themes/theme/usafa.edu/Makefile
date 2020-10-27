.PHONY: default
default: beamerthemeusafa.edu.sty example.pdf beamerthemeusafa.edu.pdf

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

beamerthemeusafa.edu.pdf: beamerthemeusafa.edu.sty example.pdf | minted
beamerthemeusafa.edu.sty: | beamercolorthemefalcon.sty

example.pdf: beamerthemeusafa.edu.sty

include $(shell git rev-parse --show-toplevel)/Makefile.mk

# fall-back for Beamer themes
beamercolorthemefalcon.sty:
	$(MAKE) --directory=../../color/falcon $@
