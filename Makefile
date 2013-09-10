BASEDIR=$(CURDIR)
DOCDIR=$(BASEDIR)/docs
DISTDIR=$(BASEDIR)/dist
PACKAGE='djangorpc'
EXAMPLEDIR='example'

help:
	@echo 'Makefile for DjangoRpc                                               '
	@echo '                                                                     '
	@echo 'Usage:                                                               '
	@echo '   make clean            Remove all temporary and generated artifacts'
	@echo '   make dist             Generate a distributable package            '
	@echo '   make doc              Generate the documentation                  '
	@echo '   make test             Run the test suite                          '
	@echo '                                                                     '

test:
	@echo 'Running test suite'
	@cd $(EXAMPLEDIR) && python manage.py test main game tricks

dist:
	@echo 'Generating a distributable python package'
	@python setup.py sdist
	@echo 'Done'

doc:
	@echo 'Generating documentation'
	@cd $(DOCDIR) && make html
	@echo 'Done'

clean:
	rm -fr $(DISTDIR)
