.PHONY: all
all: graded-review.sty graded-review.pdf

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

graded-review.sty:
graded-review.pdf: graded-review.sty | minted

include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex
