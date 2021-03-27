.PHONY: all
all: packages documentation

packages = $(patsubst %.dtx,%.sty,$(wildcard *.dtx))
documentation = $(patsubst %.dtx,%.pdf,$(wildcard *.dtx))

.PHONY: packages
packages: $(packages)

.PHONY: documentation
documentation: $(documentation)

examples:
	mkdir --parents $@

$(documentation): | examples

include $(shell git rev-parse --show-toplevel)/Makefile.mk
