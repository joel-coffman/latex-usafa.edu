documents := application.pdf

.PHONY: default
default: application.pdf


subdirs := $(patsubst %/.,%,$(wildcard */.))

# BEGIN remove for distribution
distribution := distribution
subdirs := $(filter-out $(distribution),$(subdirs))
# END remove for distribution

.PHONY: $(subdirs)
$(subdirs):
	$(MAKE) -C $@


application.pdf: | supplements


include $(shell git rev-parse --show-toplevel)/Makefile.mk
# BEGIN remove for distribution


define create-parent-directories
@mkdir --parents $$(dirname "$@")
endef

define patch-makefile
$(create-parent-directories)
sed "s|\$$(shell git rev-parse --show-toplevel)|$$(dirname $$(realpath --relative-to=$< .))|" $< | sed '/^# BEGIN remove for distribution/,/^# END remove for distribution/d' > $@
endef


files := \
        $(shell git ls-files) \
        promotion.sty \
        record.sty \
        statement.sty \
        supplements.sty \
        hyperfix.sty \
        Makefile.mk
files := $(addprefix $(distribution)/,$(files))

$(files): | $(distribution)

$(distribution)/Makefile: Makefile
	$(patch-makefile)

$(distribution)/%/Makefile: %/Makefile
	$(patch-makefile)

$(distribution)/Makefile.mk: $(shell git rev-parse --show-toplevel)/Makefile.mk
	cp $< $@

# set search path for packages: ./texmf is last resort due to its symlinks
_VPATH = $(shell cd $$(git rev-parse --show-cdup) && find . -name "*.sty" -exec dirname {} \; | sort --random-sort)
vpath %.sty $(addprefix $(shell git rev-parse --show-cdup),$(filter-out ./texmf/%,$(_VPATH)) $(filter ./texmf/%,$(_VPATH)))

$(distribution)/%.sty: %.sty
	cp $< $@

$(distribution)/%: %
	$(create-parent-directories)
	cp --dereference $< $@

$(distribution):
	mkdir --parents $@


template.zip: $(files)
	zip -r $(archive) $(distribution)


.PHONY: distcheck
distcheck: dist
	unzip -d $(directory) template.zip
	$(MAKE) -C $(directory)/$(distribution)

# target-specific variables
distcheck: directory := $(shell mktemp --directory)

.PHONY: distclean
distclean:
	$(RM) --recursive $(archive) $(distribution)
