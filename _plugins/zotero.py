import bibtexparser
from pyzotero import zotero
from scholarly import scholarly

author = scholarly.search_author_id('cyGQzsIAAAAJ')
pubs_scholar = scholarly.fill(author, sections=['publications'])

library_id = '5089770'
api_key = 'qCNPbUNmPHEunhCOKdcPkHhW'

zot = zotero.Zotero(library_id, 'user', api_key)
zot.add_parameters(format='bibtex')
pub = zot.publications()

for ent in pub.entries:
    ent['pdf'] = ent['url']

with open('_bibliography/papers.bib', 'w') as f:
	bibtexparser.dump(pub, f)
