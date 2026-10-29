"""Read-only candidate verification. Reports limited scope; never contacts GitHub/course."""
import argparse
from collections import Counter, defaultdict
import datetime as dt
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--manifest', default='MANIFEST.json')
p.add_argument('--require-node', action='store_true')
p.add_argument('--publication-ready', action='store_true', help='Also require recorded real issue URLs; performs no network actions')
a = p.parse_args()
checks = []
skipped = []

def check(name, condition, detail=None):
    checks.append({'name': name, 'passed': bool(condition), 'detail': detail})

def read(rel):
    return json.loads((ROOT / rel).read_text())

manifest = read(a.manifest)
files = manifest['files']
bad = [name for name, info in files.items() if not (ROOT / name).is_file() or
       hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != info['sha256'] or
       (ROOT / name).stat().st_size != info['bytes']]
check('Every frozen candidate file matches manifest', not bad, bad)
ignored = {'node_modules', '.single-build', '.rebuilt-site', '__pycache__', '.git'}
actual = {str(f.relative_to(ROOT)) for f in ROOT.rglob('*') if f.is_file() and
          not any(x in ignored or x.startswith('.kb-rebuild-') for x in f.relative_to(ROOT).parts)}
check('No unlisted public-candidate files', actual == set(files) | {a.manifest}, sorted(actual - set(files) - {a.manifest}))
originals = read('ORIGINALS.json')['files']
check('All original exported files remain unchanged', all(hashlib.sha256((ROOT / f).read_bytes()).hexdigest() == h for f, h in originals.items()), len(originals))

data = read('support-kb/src/lib/data/reports-4471.json')
tenants = {t['handle']: t for t in (json.loads(f.read_text()) for f in (ROOT / 'support-kb/src/lib/data/tenants').glob('*.json'))}
copies = defaultdict(list)
schema_errors = []
for i, report in enumerate(data):
    copies[report.get('id')].append(report)
    try:
        assert isinstance(report['id'], str) and re.fullmatch(r'R-\d+', report['id'])
        assert report['channel'] in {'app', 'email', 'form'}
        assert report['tenant'] in tenants
        assert isinstance(report['subject'], str) and isinstance(report['body'], str)
        assert report['meta']['intakeTag'] in {'parser', 'hint'}
        assert isinstance(report['meta']['browserLocale'], str)
        assert report['mergedInto'] == 4471
        received, merged = (dt.datetime.fromisoformat(report[k]) for k in ('receivedAt', 'mergedAt'))
        assert received.tzinfo is not None and merged.tzinfo is not None and received <= merged
    except (AssertionError, KeyError, TypeError, ValueError) as error:
        schema_errors.append({'row': i, 'id': report.get('id'), 'error': type(error).__name__})
check('Every supplied report has the expected valid schema and timestamp order', not schema_errors, schema_errors)
conflicts = [id for id, rows in copies.items() if len({json.dumps(row, sort_keys=True) for row in rows}) != 1]
check('Repeated IDs have identical complete records', not conflicts, conflicts)
unique = [rows[0] for rows in copies.values()]
check('Raw/unique/duplicate reconciliation', (len(data), len(unique), len(data) - len(unique)) == (427, 412, 15), [len(data), len(unique), len(data) - len(unique)])
check('All tenant form values are supported', all(t['form'] in {'booking-v2', 'booking-v3'} for t in tenants.values()), sorted(tenants))
locales = sorted({t['locale'] for t in tenants.values()})
node = shutil.which('node')
if node:
    code = "console.log(JSON.stringify(JSON.parse(process.argv[1]).map(locale=>{const p=new Intl.DateTimeFormat(locale,{year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date(Date.UTC(2026,0,2,12))).map(x=>x.type);return {locale,dayFirst:p.indexOf('day')<p.indexOf('month')}})))"
    run = subprocess.run([node, '-e', code, json.dumps(locales)], text=True, capture_output=True)
    orders = json.loads(run.stdout) if run.returncode == 0 else []
    check('Independent Intl check: all supplied tenant locales are day first', len(orders) == len(locales) and all(x['dayFirst'] for x in orders), orders)
else:
    skipped.append('Intl runtime check: Node is not on PATH. Snapshot locale hashes remain checked.')
    if a.require_node:
        check('Required Node runtime exists', False)

# Independently implemented reproduction of the OLD model, not independent causal proof.
by_cause = defaultdict(list)
for report in unique:
    t = tenants[report['tenant']]
    by_cause['hint' if t['form'] == 'booking-v3' and report['channel'] == 'form' else 'parser'].append(report)
check('Independent tenant/form/channel partition', {k: len(v) for k, v in by_cause.items()} == {'parser': 379, 'hint': 33}, {k: len(v) for k, v in by_cause.items()})
check('Hint tenant distribution', Counter(r['tenant'] for r in by_cause['hint']) == {'alder.physio': 12, 'copper.studio': 11, 'pale.harbour': 10})
check('Parser channel distribution', Counter(r['channel'] for r in by_cause['parser']) == {'app': 204, 'email': 150, 'form': 25})
disagree = sum(r['meta']['intakeTag'] != cause for cause, rs in by_cause.items() for r in rs)
check('Intake disagreement count', disagree == 38, disagree)
note_ids = set(read('support-kb/src/lib/data/desk-notes.json')['oneDayMove'])
check('Diagnostic IDs are included exactly once within parser', len(note_ids) == 5 and note_ids <= {r['id'] for r in by_cause['parser']}, sorted(note_ids))

problems = {
    'parser': [r for r in by_cause['parser'] if r['id'] not in note_ids],
    'hint': by_cause['hint'],
    'day-shift': [r for r in unique if r['id'] in note_ids],
    'unplaced': [],
}
check('Exclusive problem coverage is 374 parser / 33 hint / 5 investigation',
      {k: len(v) for k, v in problems.items()} == {'parser': 374, 'hint': 33, 'day-shift': 5, 'unplaced': 0})
all_ids = [r['id'] for rs in problems.values() for r in rs]
check('Every unique report belongs to exactly one proposed ticket', len(all_ids) == len(set(all_ids)) == len(unique) and set(all_ids) == set(copies))
ledger = read('evidence/report-coverage.json')
check('Coverage ledger exact ID sets match independent allocation',
      ledger['rawRows'] == len(data) and ledger['uniqueIDs'] == len(unique) and
      len(ledger['groups']) == len(problems) and
      all(g['count'] == len(problems[g['problem']]) and g['ids'] == sorted(r['id'] for r in problems[g['problem']]) for g in ledger['groups']))
check('Revised parser channel distribution', Counter(r['channel'] for r in problems['parser']) == {'app': 202, 'email': 147, 'form': 25})
check('Investigation contains the exact desk-note IDs', {r['id'] for r in problems['day-shift']} == note_ids)

page = ROOT / 'support-kb/src/routes/kb/decisions/0002-triage-by-cause/+page.svx'
source = page.read_text()
frontmatter = source.split('---', 2)[1]
for field in ('title', 'owner', 'status', 'reviewed', 'signature'):
    check('Page frontmatter: ' + field, re.search(r'^' + field + r':\s*\S', frontmatter, re.M) is not None)
check('Proposed successor preserves lifecycle and literal ending stamp', 'status: proposed' in frontmatter and source.rstrip().endswith('<RenderStamp {signature} />') and '0001' in source)
issue_names = ['01-parser.md', '02-form-hint.md', '03-day-shift.md']
issues = [(ROOT / 'issues' / name).read_text() for name in issue_names]
check('All three issue titles state correct coverage', all(f'— {n} reports from #4471' in text.splitlines()[0] for n, text in zip((374, 33, 5), issues)))
check('Investigation preserves all five original bodies', all(r['body'] in issues[2] for r in problems['day-shift']))
links = read('support-kb/src/lib/data/ticket-links.json')
check('All proposed groups have working local issue records', set(links) == {'parser', 'hint', 'day-shift'} and all((ROOT / value['draft'].lstrip('/')).is_file() for value in links.values()))
urls = [v['github'] for v in links.values()]
valid_urls = all(url is None or re.fullmatch(r'https://github\.com/davesousa/megadev-s01e03-what-it-shows/issues/[1-9][0-9]*', url) for url in urls)
check('Recorded issue URLs have the intended repo shape, without duplicates', valid_urls and len([u for u in urls if u]) == len(set(u for u in urls if u)))
if a.publication_ready:
    check('Publication requires all three real issue URLs recorded', all(urls))
check('Local publication procedure preserves separate evaluation authorization', 'Course submission requires separate authorization' in (ROOT / 'PUBLICATION.md').read_text())
check('Unsupported product mapping removed', 'supplied sched-prod' not in (ROOT / 'issues/01-parser.md').read_text())

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.text = []
        self.rows = []
        self.row = None
        self.cell = None
        self.links = []
        self.resources = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'style'}:
            self.hidden += 1
        if tag == 'tr': self.row = []
        if tag in {'td', 'th'}: self.cell = []
        if tag == 'a' and 'href' in attrs: self.links.append(attrs['href'])
        if tag in {'script', 'img', 'iframe'} and 'src' in attrs: self.resources.append(attrs['src'])
        if tag == 'link' and attrs.get('rel') in {'stylesheet', 'modulepreload'}: self.resources.append(attrs.get('href', ''))
    def handle_endtag(self, tag):
        if tag in {'script', 'style'}: self.hidden -= 1
        if tag in {'td', 'th'} and self.row is not None and self.cell is not None:
            self.row.append(' '.join(''.join(self.cell).split())); self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row); self.row = None
    def handle_data(self, text):
        if not self.hidden:
            self.text.append(text)
            if self.cell is not None: self.cell.append(text)

standalone = Page()
standalone.feed((ROOT / 'rendered/page.html').read_text())
check('Standalone rendered problem coverage', all(any(row[:2] == expected for row in standalone.rows) for expected in [
    ['Shared month-first parser', '374'], ['Booking-v3 form hint mismatch', '33'],
    ['One-day / cross-city date shifts — investigation', '5']]))
check('Standalone links all issue records', all((v['github'] or v['preview']) in standalone.links for v in links.values()))
check('Standalone shows all investigation bodies', all(r['body'] in ''.join(standalone.text) for r in problems['day-shift']))
check('Standalone stamp appears in visible markup', 'DR-4AG7-CDB9' in ''.join(standalone.text))
check('Standalone has no external markup resources', standalone.resources == [], standalone.resources)
link_errors = []
site_pages = sorted((ROOT / 'site').rglob('*.html'))
for file in site_pages:
    doc = Page(); doc.feed(file.read_text())
    for href in doc.links:
        target = ROOT / 'site' / href.lstrip('/')
        if href.startswith('/') and not target.is_file() and not (target / 'index.html').is_file():
            link_errors.append({'page': str(file.relative_to(ROOT)), 'href': href})
check('Complete site has five KB pages, three issue previews and working local routes', len(site_pages) == 8 and len(list((ROOT / 'site/kb').rglob('*.html'))) == 5 and not link_errors, link_errors)
check('Served issue drafts exactly match canonical issue bodies', all((ROOT / 'site/issues' / name).read_bytes() == (ROOT / 'issues' / name).read_bytes() for name in issue_names))
for name in issue_names:
    preview_path = ROOT / 'site/issues' / name.replace('.md', '.html')
    preview_text = preview_path.read_text()
    preview = Page(); preview.feed(preview_text)
    check('UTF-8 preview preserves exact issue prose: ' + name, '<meta charset="utf-8">' in preview_text and (ROOT / 'issues' / name).read_text() in ''.join(preview.text))
index = (ROOT / 'site/kb/index.html').read_text()
check('Native KB index discovers proposed successor', '/kb/decisions/0002-triage-by-cause' in index)
native = Page(); native.feed((ROOT / 'site/kb/decisions/0002-triage-by-cause/index.html').read_text())
check('Independent render pipelines agree on visible page content', ' '.join(' '.join(native.text).split()) == ' '.join(' '.join(standalone.text).split()))

result = {'scope': 'Frozen local candidate only; proposed problem coverage differs from the original classifier. No deployed-product proof or course acceptance.',
          'passed': all(c['passed'] for c in checks), 'checks': checks, 'skipped': skipped}
print(json.dumps(result, indent=2))
raise SystemExit(0 if result['passed'] else 1)
