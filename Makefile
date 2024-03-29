# use Bash as the shell when interpreting the Makefile
SHELL := /bin/bash


packages := $(shell comm -12 <(find . -name "*.dtx" -exec dirname {} \; | sort) <(find . -name "*.ins" -exec dirname {} \; | sort) | uniq)

.PHONY: all
all: $(packages) promotion/template

.PHONY: $(packages)
$(packages):
	$(MAKE) -C $@ dist distcheck

.PHONY: promotion/template
promotion/template: | promotion
	$(MAKE) -C $@
	$(MAKE) -C $@ dist distcheck


.PHONY: list
list:
	@for package in $(packages); do echo $$package; done
