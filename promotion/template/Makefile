documents := application.pdf

.PHONY: default
default: application.pdf


subdirs := $(patsubst %/.,%,$(wildcard */.))

.PHONY: $(subdirs)
$(subdirs):
	$(MAKE) -C $@


application.pdf: | supplements


include $(shell git rev-parse --show-toplevel)/Makefile.mk
# END Makefile for distribution


package = $(shell git ls-files)
dependencies = \
        promotion.sty \
        record.sty \
        statement.sty \
        supplements.sty \
        hyperfix.sty

distribution := $(shell mktemp --directory)

.PHONY: $(distribution)
$(distribution): $(package) $(dependencies)
	cp --dereference --parents $(package) $(distribution)/.
	cp $$(git rev-parse --show-toplevel)/Makefile.mk $(distribution)/.
	for f in $$(find . -name Makefile | sort); do \
	  sed "s|\$$(shell git rev-parse --show-toplevel)|$$(dirname $$(realpath --relative-to=$$f .))|" $$f | sed -n '/END Makefile for distribution/q;p' > $(distribution)/$$f; \
	done

%.sty:
	cp $$(find $(shell git rev-parse --show-toplevel)/texmf -name "$@") $(distribution)/.

template.zip: $(distribution)
	(cd $(distribution); zip -r $(archive) *)
	cp $(distribution)/$(archive) .


.PHONY: distcheck
distcheck: dist
	unzip -d $(directory) template.zip
	$(MAKE) -C $(directory)

# target-specific variables
distcheck: directory := $(shell mktemp --directory)
