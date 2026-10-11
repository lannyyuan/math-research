import {continueRender, delayRender, staticFile} from 'remotion';

// 字幕字体：Andika（SIL OFL 1.1，SIL 专门为初学阅读的孩子设计：a、g 是单层写法，字母易辨认）
if (typeof document !== 'undefined') {
  const handle = delayRender('load Andika');
  const faces = [
    new FontFace('AndikaSub', `url(${staticFile('fonts/andika-latin-400-normal.woff2')})`, {weight: '400'}),
    new FontFace('AndikaSub', `url(${staticFile('fonts/andika-latin-700-normal.woff2')})`, {weight: '700'}),
  ];
  Promise.all(faces.map((f) => f.load()))
    .then((loaded) => {
      loaded.forEach((f) => (document.fonts as unknown as {add: (f: FontFace) => void}).add(f));
      continueRender(handle);
    })
    .catch((e) => {
      console.error('font load failed', e);
      continueRender(handle);
    });
}
