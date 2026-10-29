"""Rebuild the candidate KB in scratch space; never edit the reviewed site or sources."""
import argparse
import html
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
p = argparse.ArgumentParser()
p.add_argument('--output', type=Path, default=ROOT / '.rebuilt-site')
p.add_argument('--node-modules', type=Path, default=ROOT / 'node_modules')
a = p.parse_args()
output = a.output.resolve()
modules = a.node_modules.resolve()
if output.exists():
    raise SystemExit('Output already exists. Choose a new directory; reviewed artifacts will not be overwritten.')
if output.is_relative_to(ROOT / 'support-kb') or output.is_relative_to(ROOT / 'site'):
    raise SystemExit('Choose scratch output outside reviewed source/site directories.')
node = shutil.which('node')
if not node or not (modules / 'vite/bin/vite.js').is_file():
    raise SystemExit('Need compatible Node on PATH and dependencies from npm ci, or --node-modules PATH.')
with tempfile.TemporaryDirectory(prefix='.kb-rebuild-', dir=ROOT) as temp:
    work = Path(temp)
    shutil.copytree(ROOT / 'support-kb/src', work / 'src')
    shutil.copytree(ROOT / 'issues', work / 'static/issues')
    # Browsers may misdecode standalone Markdown without a charset header.
    # HTML previews keep exact issue prose readable and offer related draft navigation.
    issue_files = sorted((ROOT / 'issues').glob('*.md'))
    for issue in issue_files:
        body = issue.read_text()
        title = body.splitlines()[0].removeprefix('# ')
        related = ' · '.join(f'<a href="{html.escape(other.stem)}.html">{html.escape(other.stem)}</a>' for other in issue_files)
        preview = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                   '<meta name="viewport" content="width=device-width,initial-scale=1">'
                   f'<title>{html.escape(title)} · issue draft</title>'
                   '<style>body{font:16px/1.6 system-ui,sans-serif;max-width:76ch;margin:2rem auto;padding:0 1rem}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}nav{margin-bottom:1rem}</style>'
                   '</head><body><nav><a href="/kb/decisions/0002-triage-by-cause/">Signed KB page</a> · '
                   f'<a href="{html.escape(issue.name)}" download>Download exact Markdown</a><br>{related}</nav>'
                   '<p><strong>Archived reviewed draft — the signed KB page links the filed GitHub issue.</strong></p>'
                   f'<main><pre>{html.escape(body)}</pre></main></body></html>')
        (work / 'static/issues' / (issue.stem + '.html')).write_text(preview)
    shutil.copy2(ROOT / 'tooling/app.html', work / 'src/app.html')
    shutil.copy2(ROOT / 'tooling/layout.js', work / 'src/routes/+layout.js')
    for name in ('svelte.config.js', 'vite.config.js'):
        shutil.copy2(ROOT / 'tooling' / name, work / name)
    (work / 'package.json').write_text(json.dumps({'private': True, 'type': 'module'}) + '\n')
    (work / 'node_modules').symlink_to(modules, target_is_directory=True)
    result = subprocess.run([node, str(modules / 'vite/bin/vite.js'), 'build'], cwd=work, env=os.environ.copy())
    if result.returncode:
        raise SystemExit(result.returncode)
    output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(work / 'build', output)
print(json.dumps({'site': str(output), 'htmlPages': sorted(str(p.relative_to(output)) for p in output.rglob('*.html'))}))
