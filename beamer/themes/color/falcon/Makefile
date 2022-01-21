.PHONY: all
all: beamercolorthemefalcon.sty beamercolorthemefalcon.pdf

derivatives += beamercolorthemefalcon.sty

beamercolorthemefalcon.sty:
beamercolorthemefalcon.pdf: beamercolorthemefalcon.sty example.pdf

example.pdf: beamercolorthemefalcon.sty ../../beamerthemeexamplebase.tex

include $(shell git rev-parse --show-toplevel)/Makefile.mk
