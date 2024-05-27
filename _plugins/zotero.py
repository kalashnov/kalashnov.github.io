import bibtexparser
from pyzotero import zotero

library_id = '5089770'
api_key = 'qCNPbUNmPHEunhCOKdcPkHhW'

zot = zotero.Zotero(library_id, 'user', api_key)
zot.add_parameters(format='bibtex')
pub = zot.publications()

with open('zotero.bib', 'w') as f:
	bibtexparser.dump(pub, f)
