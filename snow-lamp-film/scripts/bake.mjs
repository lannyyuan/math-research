// 烘焙大面积水彩层 → public/baked/*.png|jpg     用法： node scripts/bake.mjs [资产名 ...]
import path from 'node:path';
import fs from 'node:fs';
import {bundle} from '@remotion/bundler';
import {renderStill, selectComposition} from '@remotion/renderer';

const browserExecutable = process.env.REMOTION_BROWSER ?? '/opt/pw-browsers/chromium_headless_shell-1194/chrome-linux/headless_shell';
const outDir = path.resolve('public/baked');
fs.mkdirSync(outDir, {recursive: true});
const serveUrl = await bundle({entryPoint: path.resolve('src/index.ts'), onProgress: () => {}});
const manifestPath = path.resolve('src/bake/manifest.json');
const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
const want = process.argv.slice(2);
for (const [name, spec] of Object.entries(manifest)) {
  if (want.length && !want.includes(name)) continue;
  const inputProps = {asset: name};
  const composition = await selectComposition({serveUrl, id: 'Bake', inputProps, browserExecutable});
  const ext = spec.format === 'jpeg' ? 'jpg' : 'png';
  const output = path.join(outDir, `${name}.${ext}`);
  const t0 = Date.now();
  await renderStill({composition, serveUrl, output, frame: 0, inputProps, browserExecutable, imageFormat: spec.format, ...(spec.format === 'jpeg' ? {jpegQuality: 90} : {}), scale: 1});
  console.log(name, `${Date.now() - t0}ms`, `${(fs.statSync(output).size / 1024).toFixed(0)}KB`);
}
