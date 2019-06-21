.PHONY: default
default: graded-review.sty graded-review.pdf

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

graded-review.sty:
graded-review.pdf: graded-review.sty | minted

include ../Makefile.mk
