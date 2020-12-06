# use Bash as the shell when interpreting the Makefile
SHELL := /bin/bash


packages := $(shell comm -12 <(find . -name "*.dtx" -exec dirname {} \; | sort) <(find . -name "*.ins" -exec dirname {} \; | sort) | uniq)

.PHONY: default
default: $(packages) promotion/template

.PHONY: $(packages)
$(packages):
	$(MAKE) -C $@ dist

.PHONY: promotion/template
promotion/template: | promotion
	$(MAKE) -C $@ dist
