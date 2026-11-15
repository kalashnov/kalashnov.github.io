"""Sync Zotero "My Publications" -> _bibliography/papers.bib for al-folio.

Per item, extra al-folio fields come from:
  - Google Scholar profile, matched by title                   -> google_scholar_id, citations
  - "Link to URI" attachments titled code / blog / slides / ... -> that field
  - any attachment whose URL is on arxiv.org (e.g. arXiv snapshot) -> arxiv
  - an image attachment                                        -> preview (downloaded)
  - tags `selected` / `forthcoming`                            -> home page / ", forthcoming"
  - Zotero item key                                            -> zotero_key (blog post / summary lookup on the site)
  - item type Preprint / Manuscript                            -> preprint ("Working papers" section)
"""
import os
import pathlib
import re
import multiprocessing

import bibtexparser
from bibtexparser.bibdatabase import BibDatabase
from pyzotero import zotero
from scholarly import scholarly

LIBRARY_ID = '5089770'
SCHOLAR_USER = 'cyGQzsIAAAAJ'
PREVIEW_DIR = pathlib.Path('assets/img/publication_preview')
LINK_FIELDS = {'code', 'blog', 'slides', 'website', 'poster', 'video', 'html', 'pdf', 'supp'}
BIB = pathlib.Path('_bibliography/papers.bib')
ARXIV = re.compile(r'arxiv\.org/(?:abs|pdf)/([^?#/]+?)(?:v\d+)?(?:\.pdf)?/?$')


def norm(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())


def fetch_scholar():
    author = scholarly.fill(scholarly.search_author_id(SCHOLAR_USER), sections=['publications'])
    return {norm(p['bib']['title']): (p['author_pub_id'].split(':')[1], p.get('num_citations', 0))
            for p in author['publications']}


def scholar_ids():
    """{normalized title: (scholar id, citation count)}; {} if Scholar blocks us, so the sync still runs.

    scholarly swallows exceptions and retries forever when Scholar blocks CI runners,
    so it runs in a separate process that is killed after 120 s.
    """
    pool = multiprocessing.Pool(1)
    try:
        return pool.apply_async(fetch_scholar).get(timeout=120)
    except Exception as e:
        print(f'::warning::Google Scholar unavailable, keeping last run\'s IDs/counts: {e!r}')
        return {}
    finally:
        pool.terminate()


def main():
    zot = zotero.Zotero(LIBRARY_ID, 'user', os.environ['ZOTERO_API_KEY'])
    db = BibDatabase()
    scholar = scholar_ids()
    seen = set()
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
            if m := ARXIV.search(c.get('url', '')):
                entry['arxiv'] = m.group(1)  # al-folio wants the bare id: .../abs/2103.11066v5 -> 2103.11066
            if c.get('linkMode') == 'linked_url' and title in LINK_FIELDS:
                entry[title] = c['url']
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


if __name__ == '__main__':  # guard: the Scholar worker process re-imports this file
    main()
