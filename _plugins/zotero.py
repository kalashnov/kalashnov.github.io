import bibtexparser
from pyzotero import zotero

library_id = '5089770'
api_key = 'qCNPbUNmPHEunhCOKdcPkHhW'

zot = zotero.Zotero(library_id, 'user', api_key)
zot.add_parameters(format='bibtex')
pub = zot.publications()

with open('_bibliography/added_files.bib', 'w') as f:
	previous = f.readlines()

with open('_bibliography/zotero.bib', 'w') as f:
	f.writelines(previous)
	bibtexparser.dump(pub, f)
