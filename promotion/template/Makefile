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

directory := $(shell mktemp --directory)

.PHONY: $(directory)
$(directory): $(package) $(dependencies)
	cp --dereference --parents $(package) $(directory)/.
	cp $$(git rev-parse --show-toplevel)/Makefile.mk $(directory)/.
	for f in $$(find . -name Makefile | sort); do \
	  sed "s|\$$(shell git rev-parse --show-toplevel)|$$(dirname $$(realpath --relative-to=$$f .))|" $$f | sed -n '/END Makefile for distribution/q;p' > $(directory)/$$f; \
	done

%.sty:
	cp $$(find $(shell git rev-parse --show-toplevel)/texmf -name "$@") $(directory)/.

template.zip: $(directory)
	(cd $(directory); zip -r $(archive) *)
	cp $(directory)/$(archive) .
