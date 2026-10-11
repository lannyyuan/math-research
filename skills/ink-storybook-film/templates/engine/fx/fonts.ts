import {continueRender, delayRender, staticFile} from 'remotion';

// 字幕字体：霞鹜文楷（LXGW WenKai，SIL OFL 1.1），已裁成只含字幕用字的小文件
if (typeof document !== 'undefined') {
  const handle = delayRender('load subtitle font');
  const face = new FontFace('WenKaiSub', `url(${staticFile('fonts/WenKai-subtitle.woff2')})`);
  face
    .load()
    .then((f) => {
      (document.fonts as unknown as {add: (f: FontFace) => void}).add(f);
      continueRender(handle);
    })
    .catch((e) => {
      console.error('font load failed', e);
      continueRender(handle);
    });
}
