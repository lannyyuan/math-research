// 打印每个场景的帧范围（含首尾）：  <场景id> <起始帧> <结束帧>
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const tl = JSON.parse(fs.readFileSync(path.join(root, 'src/timeline.json'), 'utf8'));
let f = 0;
for (const sc of tl.scenes) {
  const n = Math.round(sc.len * tl.fps);
  console.log(`${sc.id} ${f} ${f + n - 1}`);
  f += n;
}
