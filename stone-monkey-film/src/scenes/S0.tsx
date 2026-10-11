import React from 'react';
import {Img, staticFile} from 'remotion';
import {W, H} from '../palette';
import {Snow} from '../fx/Snow';
import {Bg, SceneWrap, useT, lerp, ramp} from './kit';
import {CharsCtx} from '../fx/Variant';
import {useContext} from 'react';
import title from '../../public/props/title.json';

// 片头：天上那盏灯是个灰色的圆，一点光都没有。片名“小石猴点灯”从墨里慢慢显出来（封面上的书法字，按“墨晕开”的显现图一点点洇出来）。
const TZ = title.title_zh, TE = title.title_en;
export const S0: React.FC<{len: number}> = ({len}) => {
  const t = useT();
  const z = lerp(1.0, 1.06, t / len);
  const p = ramp(t, 1.8, 6.6); // 墨晕开的进度
  const S = 16; // 蒙版的陡度（越大边缘越硬）
  const tw = 920, th = (TZ.h / TZ.w) * tw;
  const ew = 520, eh = (TE.h / TE.w) * ew;
  const tx = (W - tw) / 2, ty = 566;
  const show = useContext(CharsCtx) >= 2;
  return (
    <SceneWrap len={len} fadeIn={30} fadeOut={34}>
      <div style={{position: 'absolute', inset: 0, transform: `scale(${z})`, transformOrigin: '50% 40%'}}>
        <Bg name="title_sky" w={W} h={H} />
      </div>
      {show && (
        <>
          {/* 片名：墨晕开 */}
          <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
            <defs>
              <filter id="thr" x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
                <feComponentTransfer>
                  <feFuncR type="linear" slope={-S} intercept={S * p * 1.1} />
                  <feFuncG type="linear" slope={-S} intercept={S * p * 1.1} />
                  <feFuncB type="linear" slope={-S} intercept={S * p * 1.1} />
                </feComponentTransfer>
              </filter>
              <mask id="inkmask" maskUnits="userSpaceOnUse" x={tx} y={ty} width={tw} height={th}>
                <image href={staticFile('props/title_zh_reveal.png')} x={tx} y={ty} width={tw} height={th} filter="url(#thr)" preserveAspectRatio="none" />
              </mask>
              <filter id="soft"><feGaussianBlur stdDeviation="5" /></filter>
            </defs>
            <g mask="url(#inkmask)">
              <image href={staticFile('props/title_zh.png')} x={tx} y={ty} width={tw} height={th} filter="url(#soft)" opacity={0.28} preserveAspectRatio="none" />
              <image href={staticFile('props/title_zh.png')} x={tx} y={ty} width={tw} height={th} preserveAspectRatio="none" />
            </g>
          </svg>
          <Img src={staticFile('props/title_en.png')} style={{position: 'absolute', left: (W - ew) / 2, top: ty + th + 34, width: ew, height: eh, opacity: 0.85 * ramp(t, 5.4, 7.6)}} />
        </>
      )}
      <Snow amount={0.5} wind={0.04} speed={0.55} />
    </SceneWrap>
  );
};
