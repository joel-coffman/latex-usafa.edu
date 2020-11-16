SUBDIRS := $(wildcard */.)

.PHONY: default
default: promotion $(SUBDIRS) \
         $(patsubst %.tex,%.pdf,$(wildcard *.tex))

.PHONY: promotion
promotion:
	$(MAKE) -C $(shell git rev-parse --show-toplevel) $@

.PHONY: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@


include $(shell git rev-parse --show-toplevel)/Makefile.mk
