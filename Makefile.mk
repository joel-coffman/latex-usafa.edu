# use Bash as the shell when interpreting the Makefile
SHELL := /bin/bash

# function to determine the current (included) Makefile
where-am-i = $(word $(words $(MAKEFILE_LIST)), $(MAKEFILE_LIST))
# location of this Makefile (presumably the root directory of a project)
CWD := $(dir $(call where-am-i))

# empty recipes to avoid rebuilding Makefiles via implicit rules
Makefile: ;
$(CWD)Makefile.mk: ;

# add texmf directory to TEXINPUTS environment variable to find included files
# (e.g., packages)
export TEXINPUTS := .:$(CWD)texmf//:${TEXINPUTS}

# define TEX as pdflatex
TEX=pdflatex -shell-escape #-interaction batchmode

# Define a "Canned Recipe" for compiling PDFs from *.{dtx,tex} files.
#
# NOTE: OS X provides GNU Make 3.81, which does not support an assignment token
#       after `define' (see https://goo.gl/tml4Zi). If omitted, make assumes
#       it to be '='.
define compile-doc
$(TEX) -draftmode $<
if grep -E '^\\@istfilename' $*.aux; then \
		makeglossaries $*; \
fi
files=$$(sed -n 's/\\@input{\(.*\)}/\1/p' $*.aux); \
		if grep --quiet -E '\\(citation)' $*.aux $$files; then \
			bibtex $*; \
		fi
$(TEX) -draftmode $<
if [ -f $*.idx ]; then makeindex -s gind.ist -o $*.ind $*.idx; fi
if [ -f $*.glo ]; then makeindex -s $$(if [[ $< == *.dtx ]]; then echo gglo; else echo $*; fi).ist -o $*.gls $*.glo; fi
$(TEX) $<
while ( grep -q '^LaTeX Warning: Label(s) may have changed' $*.log ) do \
    $(TEX) $<; \
done
endef

DEPENDENCIES = $(wildcard *.cls) $(wildcard *.sty) \
               $(wildcard $(CWD)glossary.tex) $(wildcard $(CWD)references.bib)

%.pdf: %.dtx $(DEPENDENCIES) .version.tex
	$(compile-doc)

%.pdf: %.tex $(DEPENDENCIES) $(shell find . -mindepth 2 -name "*.tex")
	$(compile-doc)

%.sty: %.ins %.dtx
	$(TEX) -draftmode $<

# fall-back for other packages (must appear at end to avoid infinite recursion)
%.sty: $(CWD)%
	$(MAKE) --directory=$< $@


derivatives += *.acn *.acr *.alg *.aux *.bbl *.blg *.dvi *.glb *.glx *.glg *.glo *.gls *.idx *.ind *.ilg *.ist *.log *.lof *.lot *.nav *.out *.pyg *.snm *.toc *.vrb

.PHONY: clean
clean:
	$(RM) $(derivatives)

.PHONY: veryclean
veryclean: clean
	$(RM) *.pdf

.PHONY: force
force: veryclean default


ifneq ($(shell git rev-parse --show-toplevel 2> /dev/null),)
VERSION:=$(shell git describe --abbrev=12 --always --dirty=+ | sed 's/.*/\\\\providecommand{\\\\version}{&}/')
endif

.PHONY: .version
.version:
	[ -f $@.tex ] || touch $@.tex
	echo "$(VERSION)" | cmp -s $@.tex - || echo "$(VERSION)" > $@.tex

.version.tex: .version
