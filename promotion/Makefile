include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex

minted:
	if ! [ -d $@ ]; then mkdir --parents $@; fi

promotion.pdf: promotion.sty record.sty statement.sty supplements.sty | minted
record.pdf: record.sty | minted
statement.pdf: statement.sty | minted
supplements.pdf: supplements.sty | minted record.pdf statement.pdf
