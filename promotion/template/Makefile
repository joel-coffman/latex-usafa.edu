documents := application.pdf

.PHONY: all
all: application.pdf


subdirs := $(patsubst %/.,%,$(wildcard */.))

# BEGIN remove for distribution
_distribution := template
distribution := _$(_distribution)
subdirs := $(filter-out $(distribution),$(subdirs))
# END remove for distribution

.PHONY: $(subdirs)
$(subdirs):
	$(MAKE) -C $@


application.pdf: | supplements


include $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex
# BEGIN remove for distribution


define create-parent-directories
@mkdir --parents $$(dirname "$@")
endef

define patch-makefile
$(create-parent-directories)
sed "s|\$$(shell git rev-parse --show-toplevel)/texmf|$$(dirname $$(realpath --relative-to=$< .))|" $< | sed '/^# BEGIN remove for distribution/,/^# END remove for distribution/d' > $@
endef


files := \
        $(shell git ls-files) \
        promotion.sty \
        record.sty \
        statement.sty \
        supplements.sty \
        hyperfix.sty \
        Makefile.tex
files := $(addprefix $(distribution)/,$(files))

$(files): | $(distribution)

$(distribution)/Makefile: Makefile
	$(patch-makefile)

$(distribution)/%/Makefile: %/Makefile
	$(patch-makefile)

$(distribution)/Makefile.tex: $(shell git rev-parse --show-toplevel)/texmf/Makefile.tex
	cp $< $@

# set search path for packages: ./texmf is last resort due to its symlinks
_VPATH = $(shell cd $$(git rev-parse --show-cdup) && find . -name "*.sty" -exec dirname {} \; | sort | uniq)
vpath %.sty $(addprefix $(shell git rev-parse --show-cdup),$(filter-out ./texmf/%,$(_VPATH)) $(filter ./texmf/%,$(_VPATH)))

$(distribution)/%.sty: %.sty
	cp $< $@

$(distribution)/%: %
	$(create-parent-directories)
	cp --dereference $< $@

$(distribution):
	mkdir --parents $@


template.zip: $(files)
	cp --recursive $(distribution) $(directory)/$(_distribution)
	cd $(directory) && zip -r $@ $(_distribution)
	mv $(directory)/$@ $@
	$(RM) --recursive $(directory)

# target-specific variables
template.zip: directory := $(shell mktemp --directory)


.PHONY: distcheck
distcheck: dist
	unzip -d $(directory) template.zip
	$(MAKE) -C $(directory)/$(_distribution)
	$(RM) --recursive $(directory)

# target-specific variables
distcheck: directory := $(shell mktemp --directory)

_dist_derivatives += $(distribution)
