SPHINXOPTS    =
SPHINXBUILD   = sphinx-build
BUILDDIR      = _build
ALLSPHINXOPTS   = $(SPHINXOPTS) .

.PHONY: clean html 

html:
	$(SPHINXBUILD) -b html $(ALLSPHINXOPTS) $(BUILDDIR)/html
	@echo
	@echo "Build finished. The HTML pages are in $(BUILDDIR)/html."

clean:
	rm -rf $(BUILDDIR)/*
