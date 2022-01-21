# use Bash as the shell when interpreting the Makefile
SHELL := /bin/bash


reports := $(shell find * -mindepth 1 -name "Makefile" -exec dirname {} \; | sort)

.PHONY: all
all: $(reports)

.PHONY: $(reports)
$(reports):
	$(MAKE) -C $@

.PHONY: mostlyclean
mostlyclean:
	@for report in $(reports); do $(MAKE) --directory=$$report mostlyclean; done

.PHONY: clean
clean:
	@for report in $(reports); do $(MAKE) --directory=$$report clean; done
