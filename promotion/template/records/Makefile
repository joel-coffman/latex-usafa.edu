.PHONY: default
default: $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: promotion
promotion:
	$(MAKE) -C $(shell git rev-parse --show-toplevel) $@


export TEXINPUTS := ../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/Makefile.mk
