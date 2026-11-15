"""Sync Zotero "My Publications" -> _bibliography/papers.bib for al-folio.

Per item, extra al-folio fields come from:
  - Google Scholar profile, matched by title                   -> google_scholar_id, citations
  - "Link to URI" attachments titled code / blog / arXiv / ... -> that field
  - an image attachment                                        -> preview (downloaded)
  - tags `selected` / `forthcoming`                            -> home page / ", forthcoming"
  - Zotero item key                                            -> zotero_key (blog post / summary lookup on the site)
  - item type Preprint / Manuscript                            -> preprint ("Working papers" section)
"""
import os
import pathlib
import re
import signal

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from pyzotero import zotero
from scholarly import scholarly

LIBRARY_ID = '5089770'
SCHOLAR_USER = 'cyGQzsIAAAAJ'
PREVIEW_DIR = pathlib.Path('assets/img/publication_preview')
LINK_FIELDS = {'code', 'blog', 'slides', 'website', 'poster', 'video', 'html', 'pdf', 'supp', 'arxiv'}


def norm(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())


def scholar_ids():
    """{normalized title: (scholar id, citation count)}; {} if Scholar blocks us, so the sync still runs."""
    def give_up(*_):
        raise TimeoutError('no answer in 120 s')

    # scholarly retries forever when Scholar blocks CI runners; cap it
    signal.signal(signal.SIGALRM, give_up)
    signal.alarm(120)
    try:
        author = scholarly.fill(scholarly.search_author_id(SCHOLAR_USER), sections=['publications'])
    except Exception as e:
        print(f'::warning::Google Scholar unavailable, no citation counts this run: {e}')
        return {}
    finally:
        signal.alarm(0)
    return {norm(p['bib']['title']): (p['author_pub_id'].split(':')[1], p.get('num_citations', 0))
            for p in author['publications']}


zot = zotero.Zotero(LIBRARY_ID, 'user', os.environ['ZOTERO_API_KEY'])
db = BibDatabase()
scholar = scholar_ids()
seen = set()
BIB = pathlib.Path('_bibliography/papers.bib')
# last run's Scholar data, kept for papers Scholar didn't answer for this time
previous = {e['zotero_key']: e for e in bibtexparser.loads(BIB.read_text()).entries if 'zotero_key' in e}

for item in zot.everything(zot.publications(include='bibtex,data')):
    data = item['data']
    if data['itemType'] in ('attachment', 'note'):
        continue
    entry = bibtexparser.loads(item['bibtex']).entries[0]
    entry['zotero_key'] = data['key']
    seen.add(norm(data['title']))
    if norm(data['title']) in scholar:
        entry['google_scholar_id'], n = scholar[norm(data['title'])]
        entry['citations'] = str(n)
    else:
        old = previous.get(data['key'], {})
        entry.update({k: old[k] for k in ('google_scholar_id', 'citations') if k in old})

    for child in zot.children(data['key']):
        c = child['data']
        title = c.get('title', '').strip().lower()
        if c.get('linkMode') == 'linked_url' and title in LINK_FIELDS:
            # al-folio wants a bare arXiv id: https://arxiv.org/abs/2103.11066v5 -> 2103.11066v5
            entry[title] = c['url'].rstrip('/').split('/abs/')[-1] if title == 'arxiv' else c['url']
        elif c.get('contentType', '').startswith('image/'):
            name = data['key'] + pathlib.Path(c['filename']).suffix
            zot.dump(c['key'], name, str(PREVIEW_DIR))
            entry['preview'] = name

    if data['itemType'] in ('preprint', 'manuscript'):
        entry['preprint'] = 'true'
    tags = {t['tag'].lower() for t in data['tags']}
    if 'selected' in tags:
        entry['selected'] = 'true'
    if 'forthcoming' in tags:
        entry['additional_info'] = ', forthcoming'
    entry.pop('note', None)  # Zotero exports Extra as `note`; al-folio would print it
    db.entries.append(entry)

for t in scholar.keys() - seen:
    print(f'::warning::On Google Scholar but not in Zotero My Publications: {t}')

BIB.write_text(bibtexparser.dumps(db))
