include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

graded-review.sty:
graded-review.pdf: graded-review.sty | minted
