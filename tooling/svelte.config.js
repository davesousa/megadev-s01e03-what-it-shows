import adapter from '@sveltejs/adapter-static';
import { mdsvex } from 'mdsvex';
import path from 'node:path';

export default {
  extensions: ['.svelte', '.svx'],
  preprocess: mdsvex({ extensions: ['.svx'], layout: { runbook: path.resolve('src/lib/layouts/runbook.svelte') } }),
  kit: {
    adapter: adapter(),
    alias: { '#lib': './src/lib' },
    prerender: { entries: ['*'] },
  },
};
