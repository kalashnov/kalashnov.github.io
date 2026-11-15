"""Zotero "My Publications" -> data/papers.yml for the Research page (publications.qmd, _partials/papers.ejs).

    python scripts/zotero_sync.py             # from Zotero (needs ZOTERO_API_KEY)
    python scripts/zotero_sync.py --from-bib  # from the Jekyll site's _bibliography/papers.bib (no API key)

Per item, the fields come from:
  - Zotero's BibTeX export                                      -> title, authors, journal, doi, url, year, abstract
  - Google Scholar profile, matched by title                   -> scholar id + citations (last run's if Scholar fails)
  - "Link to URI" attachments titled code / blog / slides / ... -> that link
  - any attachment whose URL is on arxiv.org (e.g. arXiv snapshot) -> arxiv
  - an image attachment                                        -> preview (downloaded to images/previews/)
  - tags `selected` / `forthcoming` / `field: X`               -> About page / ", forthcoming" / "by field" view
  - Extra field (only the one-line summary goes there)         -> summary
  - item type Preprint / Manuscript                            -> status working ("Working papers"),
    or wip ("Work in progress") when there is no public draft (no `pdf` link, no arXiv)
  - newest post in posts/*/index.qmd with `paper: <Zotero key>` -> "tutorial" link
Both modes build the same BibTeX-style entries; to_paper() turns one into a papers.yml entry.
"""
import multiprocessing
import os
import pathlib
import re
import sys
import unicodedata

import bibtexparser
from bibtexparser.customization import convert_to_unicode
import yaml

LIBRARY_ID = '5089770'
SCHOLAR_USER = 'cyGQzsIAAAAJ'
ME = ('Georgy', 'Kalashnov')
ROOT = pathlib.Path(__file__).resolve().parent.parent  # quarto/
PREVIEW_DIR = ROOT / 'images/previews'
PAPERS = ROOT / 'data/papers.yml'
COAUTHORS = yaml.safe_load((ROOT / 'data/coauthors.yml').read_text())
OLD_BIB = ROOT.parent / '_bibliography/papers.bib'
LINK_FIELDS = {'code', 'blog', 'slides', 'website', 'poster', 'video', 'html', 'pdf', 'supp'}
# links row order after "published version" and arxiv: (bib field, label)
LINKS = [('pdf', 'pdf'), ('blog', 'tutorial'), ('code', 'code'), ('slides', 'slides'), ('poster', 'poster'),
         ('supp', 'appendix'), ('video', 'video'), ('website', 'website')]
ARXIV = re.compile(r'arxiv\.org/(?:abs|pdf)/([^?#/]+?)(?:v\d+)?(?:\.pdf)?/?$')


def norm(title):
    return re.sub(r'[^a-z0-9]', '', title.lower())


def clean(s):
    """BibTeX value -> plain text: {Russia} -> Russia, \\& -> &."""
    return re.sub(r'[{}]', '', s).replace('\\&', '&').strip()


def plain(s):
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()


def coauthor(name):
    """'Munro, Evan' -> {name: Evan Munro, url: ...} (url from data/coauthors.yml); None for me."""
    last, _, first = (clean(p) for p in name.partition(','))
    if (first, last) == ME:
        return None
    url = next((c['url'] for c in COAUTHORS.get(plain(last), []) if first in c['firstname']), None)
    return {'name': f'{first} {last}', **({'url': url} if url else {})}


def tutorials():
    """{Zotero key: /posts/<slug>/} from the `paper:` front matter field; the newest post wins."""
    found = {}
    for qmd in sorted(ROOT.glob('posts/*/index.qmd')):  # slugs start with the date: newest last
        if m := re.search(r'\A---\n.*?^paper:\s*["\']?(\w+)', qmd.read_text(), re.S | re.M):
            found[m.group(1)] = f'/posts/{qmd.parent.name}/'
    return found


def to_paper(e, posts):
    """One BibTeX-style entry (plus the extra fields above) -> one papers.yml entry, display decisions included."""
    e = {k: clean(v) if k != 'author' else v for k, v in convert_to_unicode(dict(e)).items()}
    doi, arxiv, url = e.get('doi'), e.get('arxiv'), e.get('url', '')
    preprint = e.get('preprint') == 'true'
    links = []
    if not preprint:
        if doi:
            links.append({'label': 'published version', 'url': f'https://doi.org/{doi}'})
        elif '://' in url and 'arxiv.org' not in url:
            links.append({'label': 'published version', 'url': url})
    if arxiv:
        links.append({'label': 'arxiv', 'url': f'https://arxiv.org/abs/{arxiv}'})
    for field, label in LINKS:
        if link := e.get(field) or (field == 'blog' and posts.get(e['zotero_key'])):
            links.append({'label': label, 'url': link})
    venue = e.get('journal') if e['ENTRYTYPE'] == 'article' else \
        e.get('booktitle') if e['ENTRYTYPE'] in ('inproceedings', 'incollection') else None
    paper = {
        'key': e['zotero_key'],
        'title': e['title'],
        'url': f'https://doi.org/{doi}' if doi else f'https://arxiv.org/abs/{arxiv}' if arxiv else url or None,
        'coauthors': [c for a in e.get('author', '').split(' and ') if a and (c := coauthor(a))],
        'venue': (venue or '') + (', forthcoming' if e.get('additional_info') == ', forthcoming' else ''),
        'year': int(e['year']) if e.get('year') else None,
        'status': 'wip' if e.get('wip') == 'true' else 'working' if preprint else 'published',
        'field': e.get('field'),
        'selected': e.get('selected') == 'true',
        'summary': e.get('summary'),
        'abstract': e.get('abstract'),
        'preview': e.get('preview'),
        'links': links,
        'scholar': {'id': e['google_scholar_id'], 'citations': int(e['citations'])}
        if e.get('google_scholar_id') else None,
    }
    return {k: v for k, v in paper.items() if v is not None}


def write(entries):
    posts = tutorials()
    papers = [to_paper(e, posts) for e in entries]
    PAPERS.write_text(yaml.safe_dump(papers, sort_keys=False, allow_unicode=True, width=10**6))
    print(f'{PAPERS}: {len(papers)} papers')


def fetch_scholar():
    from scholarly import scholarly
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


def from_zotero():
    from pyzotero import zotero
    zot = zotero.Zotero(LIBRARY_ID, 'user', os.environ['ZOTERO_API_KEY'])
    scholar = scholar_ids()
    seen = set()
    # last run's Scholar data, kept for papers Scholar didn't answer for this time
    previous = {p['key']: p['scholar'] for p in yaml.safe_load(PAPERS.read_text()) or [] if 'scholar' in p} \
        if PAPERS.exists() else {}
    entries = []

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
        elif old := previous.get(data['key']):
            entry['google_scholar_id'], entry['citations'] = old['id'], str(old['citations'])

        for child in zot.children(data['key']):
            c = child['data']
            title = c.get('title', '').strip().lower()
            if m := ARXIV.search(c.get('url', '')):
                entry['arxiv'] = m.group(1)  # bare id: .../abs/2103.11066v5 -> 2103.11066
            if c.get('linkMode') == 'linked_url' and title in LINK_FIELDS:
                entry[title] = c['url']
            elif c.get('contentType', '').startswith('image/'):
                name = data['key'] + pathlib.Path(c['filename']).suffix
                zot.dump(c['key'], name, str(PREVIEW_DIR))
                entry['preview'] = name

        if data['itemType'] in ('preprint', 'manuscript'):
            entry['preprint'] = 'true'
            # no draft to read yet -> "Work in progress" instead of "Working papers"
            if not (entry.get('pdf') or entry.get('arxiv')):
                entry['wip'] = 'true'
        # the public My Publications endpoint omits tags; read them from the library item
        raw_tags = [t['tag'] for t in zot.item(data['key'])['data']['tags']]
        tags = {t.lower() for t in raw_tags}
        for t in raw_tags:
            if t.lower().startswith('field:'):
                entry['field'] = t.split(':', 1)[1].strip()
        if 'selected' in tags:
            entry['selected'] = 'true'
        if 'forthcoming' in tags:
            entry['additional_info'] = ', forthcoming'
        if data.get('extra', '').strip():
            entry['summary'] = data['extra'].strip()  # Extra holds only the one-line summary
        entries.append(entry)

    for t in scholar.keys() - seen:
        print(f'::warning::On Google Scholar but not in Zotero My Publications: {t}')
    write(entries)


if __name__ == '__main__':  # guard: the Scholar worker process re-imports this file
    if '--from-bib' in sys.argv:
        write(bibtexparser.loads(OLD_BIB.read_text()).entries)
    else:
        from_zotero()
