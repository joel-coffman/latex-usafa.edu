documents := application.pdf

.PHONY: default
default: application.pdf


subdirs := $(patsubst %/.,%,$(wildcard */.))

.PHONY: $(subdirs)
$(subdirs):
	$(MAKE) -C $@


application.pdf: | supplements


include $(shell git rev-parse --show-toplevel)/Makefile.mk


# NOTE: Remove promotion prerequisite and target before use
#   The following rules ensure that the template builds the promotion bundle of
# packages *before* attempting to compile the application. These rules are
# necessary for the template to use the latest version of those packages, such
# as when editing the packages in the latex-usafa.edu repository.
#   When using this template "stand alone" (i.e., as the starting point for an
# application for academic promotion), the promotion bundle should be installed
# separately -- e.g., placing its packages in this directory (or in a directory
# referenced by TEXINPUTS). In that case, the following rules are unnecessary
# and will result in errors when executing `make`.
application.pdf: | promotion

.PHONY: promotion
promotion:
	$(MAKE) -C $(shell git rev-parse --show-toplevel) $@
