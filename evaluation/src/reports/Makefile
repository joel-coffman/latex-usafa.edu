# use Bash as the shell when interpreting the Makefile
SHELL := /bin/bash


reports := $(shell find * -mindepth 1 -name "Makefile" -exec dirname {} \; | sort)

.PHONY: all
all: $(reports)

.PHONY: $(reports)
$(reports):
	$(MAKE) -C $@
