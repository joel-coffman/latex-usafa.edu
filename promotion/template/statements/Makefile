documents := $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: default
default: $(documents)


export TEXINPUTS := ../:${TEXINPUTS}

include $(shell git rev-parse --show-toplevel)/Makefile.mk


# NOTE: Remove promotion prerequisite and target before use
$(documents): | promotion

.PHONY: promotion
promotion:
	$(MAKE) -C $(shell git rev-parse --show-toplevel) $@
