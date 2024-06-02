import bibtexparser
from pyzotero import zotero
from scholarly import scholarly
import yaml

author = scholarly.search_author_id('cyGQzsIAAAAJ')
pubs_scholar = scholarly.fill(author, sections=['publications'])

library_id = '5089770'
api_key = 'qCNPbUNmPHEunhCOKdcPkHhW'

zot_bib = zotero.Zotero(library_id, 'user', api_key)
zot_bib.add_parameters(format='bibtex')
pub_bib = zot_bib.publications()

for ent_bib in pub_bib.entries:
    ent_bib['pdf'] = ent_bib['url']
    note = ent_bib.get('note', '{}')
    ent_bib.pop('note', None)
    note = note.replace('\\', '')
    note = yaml.safe_load(note)
    ent_bib.update(note)

with open('_bibliography/papers.bib', 'w') as f:
	bibtexparser.dump(pub_bib, f)
