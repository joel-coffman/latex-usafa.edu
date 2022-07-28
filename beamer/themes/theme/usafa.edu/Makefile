include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

example.pdf: beamerthemeusafa.edu.sty ../../beamerthemeexamplebase.tex
