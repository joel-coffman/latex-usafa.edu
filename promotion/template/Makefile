SUBDIRS := $(patsubst %/.,%,$(wildcard */.))

.PHONY: default
default: promotion application.pdf

.PHONY: promotion
promotion:
	$(MAKE) -C $(shell git rev-parse --show-toplevel) $@

.PHONY: $(SUBDIRS)
$(SUBDIRS):
	$(MAKE) -C $@


application.pdf: | supplements


include $(shell git rev-parse --show-toplevel)/Makefile.mk
