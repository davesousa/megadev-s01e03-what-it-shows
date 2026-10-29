import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { build } from 'esbuild';
import { compile, preprocess } from 'svelte/compiler';
import { mdsvex } from 'mdsvex';
import { render } from 'svelte/server';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const lib = path.resolve(root, process.env.KB_LIB_ROOT || 'support-kb/src/lib');
const output = path.resolve(process.env.KB_RENDER_OUT || path.join(root, '.single-build'));
const entry = process.argv[2] ? path.resolve(root, process.argv[2]) : path.join(root, 'support-kb/src/routes/kb/decisions/0002-triage-by-cause/+page.svx');
await fs.mkdir(output, { recursive: true });
const css = new Set();
const warnings = [];
const markdown = mdsvex({
  extensions: ['.svx'],
  layout: { runbook: path.join(lib, 'layouts/runbook.svelte') },
});

function sveltePlugin(generate) {
  return {
    name: 'local-svelte-probe',
    setup(builder) {
      builder.onLoad({ filter: /locales\.ts$/ }, async args => {
        let source = await fs.readFile(args.path, 'utf8');
        const files = (await fs.readdir(path.join(lib, 'data/tenants'))).filter(f => f.endsWith('.json')).sort();
        const imports = files.map((f, i) => `import tenant${i} from ${JSON.stringify(path.join(lib, 'data/tenants', f))};`).join('\n');
        const entries = files.map((f, i) => `${JSON.stringify('/src/lib/data/tenants/' + f)}: tenant${i}`).join(',');
        source = source.replace("import.meta.glob<Tenant>('/src/lib/data/tenants/*.json', { eager: true, import: 'default' })", `{${entries}}`);
        return { contents: imports + '\n' + source, loader: 'ts', resolveDir: path.dirname(args.path) };
      });
      builder.onLoad({ filter: /\.(svelte|svx)$/ }, async args => {
        let source = await fs.readFile(args.path, 'utf8');
        if (args.path.endsWith('.svx')) {
          source = (await preprocess(source, markdown, { filename: args.path })).code;
        }
        const result = compile(source, {
          filename: args.path, generate, css: 'external',
        });
        if (result.css?.code) css.add(result.css.code);
        warnings.push(...result.warnings.map(w => ({ code: w.code, message: w.message })));
        return { contents: result.js.code, loader: 'js', resolveDir: path.dirname(args.path) };
      });
    },
  };
}

await build({
  entryPoints: [entry],
  outfile: path.join(output, 'sample.mjs'),
  bundle: true, platform: 'node', format: 'esm',
  alias: { '#lib': lib }, nodePaths: [path.join(root, 'node_modules')],
  packages: 'external', plugins: [sveltePlugin('server')],
});
await fs.writeFile(path.join(output, 'client-entry.mjs'),
  `import { hydrate } from 'svelte';\nimport Page from ${JSON.stringify(entry)};\nhydrate(Page, { target: document.getElementById('app') });\n`);
await build({
  entryPoints: [path.join(output, 'client-entry.mjs')],
  outfile: path.join(output, 'client.js'), bundle: true,
  alias: { '#lib': lib }, nodePaths: [path.join(root, 'node_modules')],
  platform: 'browser', format: 'esm', plugins: [sveltePlugin('client')],
});
const { default: Page } = await import(path.join(output, 'sample.mjs'));
const rendered = await render(Page);
const html = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">${rendered.head}<style>${[...css].join('\n')}</style></head><body><div id="app">${rendered.body}</div><script type="module" src="./client.js"></script></body></html>`;
await fs.writeFile(path.join(output, 'index.html'), html);
for (const text of ['desk ref', 'DR-']) {
  if (!html.includes(text)) throw new Error(`Missing rendered output: ${text}`);
}
const evidence = { utc: new Date().toISOString(), entry, lib, sample: 'selected candidate page; snapshot data', serverRenderPassed: true, clientBundleBuilt: true, warnings };
await fs.writeFile(path.join(output, 'render-result.json'), JSON.stringify(evidence, null, 2));
const client = (await fs.readFile(path.join(output, 'client.js'), 'utf8')).replaceAll('</script', '<\\/script');
await fs.writeFile(path.join(output, 'standalone.html'), html.replace('<script type="module" src="./client.js"></script>', '<script type="module">' + client + '</script>'));

console.log(JSON.stringify(evidence, null, 2));
