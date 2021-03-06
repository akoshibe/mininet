MININET = mininet/*.py
TEST = mininet/test/*.py
EXAMPLES = mininet/examples/*.py
MN = bin/mn
PYMN = $(PYTHON) -B bin/mn
BIN = $(MN)
PYSRC = $(MININET) $(TEST) $(EXAMPLES) $(BIN)
MNEXEC = mnexec
MANPAGES = mn.1 mnexec.1
P8IGN = E251,E201,E302,E202,E126,E127,E203,E226
DOCDIRS = doc/html doc/latex
PDF = doc/latex/refman.pdf

CFLAGS += -Wall -Wextra

BINDIR = `./os bindir`
MANDIR = `./os mandir`
PKGDIR = `./os pkgdir`
PYTHON = `./os python`
MNXDEP = `./os mnxdep`

all: codecheck test

clean:
	rm -rf config.mk util/install.sh build dist *.egg-info *.pyc \
	$(MNEXEC) $(MANPAGES) $(DOCDIRS) mnexec_deps.c

codecheck: $(PYSRC)
	-echo "Running code check"
	util/versioncheck.py
	pyflakes $(PYSRC)
	pylint --rcfile=.pylint $(PYSRC)
#	Exclude miniedit from pep8 checking for now
	pep8 --repeat --ignore=$(P8IGN) `ls $(PYSRC) | grep -v miniedit.py`

errcheck: $(PYSRC)
	-echo "Running check for errors only"
	pyflakes $(PYSRC)
	pylint -E --rcfile=.pylint $(PYSRC)

test: $(MININET) $(TEST)
	-echo "Running tests"
	mininet/test/test_nets.py
	mininet/test/test_hifi.py

slowtest: $(MININET)
	-echo "Running slower tests (walkthrough, examples)"
	mininet/test/test_walkthrough.py -v
	mininet/examples/test/runner.py -v

depends:
	ln -s $(MNXDEP) mnexec_deps.c

mnexec: depends mnexec.c mnexec_deps.c $(MN) mininet/net.py
	cc $(CFLAGS) $(LDFLAGS) \
	-DVERSION=\"`PYTHONPATH=. `$(PYTHON)` -B $(MN) --version`\" \
	mnexec.c mnexec_deps.c -o $@

install: $(MNEXEC) $(MANPAGES)
	install $(MNEXEC) $(BINDIR)
	install $(MANPAGES) $(MANDIR)
	$(PYTHON) setup.py install

uninstall:
	rm -rf $(BINDIR)/$(MNEXEC) $(BINDIR)/mn $(PKGDIR)/mininet-*.egg
	printf $(MANDIR)'/%s\n' $(MANPAGES) | xargs rm

develop: $(MNEXEC) $(MANPAGES)
# 	Perhaps we should link these as well
	install $(MNEXEC) $(BINDIR)
	install $(MANPAGES) $(MANDIR)
	$(PYTHON) setup.py develop

man: $(MANPAGES)

mn.1: $(MN)
	PYTHONPATH=. help2man -N -n "create a Mininet network." \
	--no-discard-stderr "$(PYMN)" -o $@

mnexec.1: $(MNEXEC)
	help2man -N -n "execution utility for Mininet." \
	-h "-h" -v "-v" --no-discard-stderr ./$(MNEXEC) -o $@

.PHONY: doc

doc: man
	doxygen doc/doxygen.cfg
	make -C doc/latex
