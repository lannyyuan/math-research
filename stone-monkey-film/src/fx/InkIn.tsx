import React, {useId} from 'react';
import {staticFile} from 'remotion';
import {W, H} from '../palette';

/**
 * 水墨晕染转场：children 这个镜头从某一点开始，像墨滴洇开一样盖在前一个镜头上。
 * p：0~1 的进度；map：显现图 a/b/c/d（洇开的起点不同）。边缘有一圈淡淡的墨色。
 */
export const InkIn: React.FC<{p: number; map?: 'a' | 'b' | 'c' | 'd'; children: React.ReactNode}> = ({p, map = 'a', children}) => {
  const id = useId().replace(/:/g, '');
  if (p <= 0.001) return null;
  if (p >= 0.999) return <>{children}</>;
  const S = 11;
  const q = p * 1.12 - 0.03;
  const href = staticFile(`props/ink_${map}.png`);
  return (
    <svg width={W} height={H} style={{position: 'absolute', left: 0, top: 0}}>
      <defs>
        <filter id={`t${id}`} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feComponentTransfer>
            <feFuncR type="linear" slope={-S} intercept={S * q} />
            <feFuncG type="linear" slope={-S} intercept={S * q} />
            <feFuncB type="linear" slope={-S} intercept={S * q} />
          </feComponentTransfer>
        </filter>
        <filter id={`r${id}`} x="0" y="0" width="100%" height="100%" colorInterpolationFilters="sRGB">
          <feComponentTransfer in="SourceGraphic" result="a">
            <feFuncR type="linear" slope={-S} intercept={S * q} />
            <feFuncG type="linear" slope={-S} intercept={S * q} />
            <feFuncB type="linear" slope={-S} intercept={S * q} />
          </feComponentTransfer>
          <feComponentTransfer in="SourceGraphic" result="b">
            <feFuncR type="linear" slope={-S} intercept={S * (q - 0.07)} />
            <feFuncG type="linear" slope={-S} intercept={S * (q - 0.07)} />
            <feFuncB type="linear" slope={-S} intercept={S * (q - 0.07)} />
          </feComponentTransfer>
          <feComposite in="a" in2="b" operator="arithmetic" k1="0" k2="1" k3="-1" k4="0" />
        </filter>
        <mask id={`m${id}`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          <image href={href} x={0} y={0} width={W} height={H} filter={`url(#t${id})`} preserveAspectRatio="none" />
        </mask>
        <mask id={`k${id}`} maskUnits="userSpaceOnUse" x={0} y={0} width={W} height={H}>
          <image href={href} x={0} y={0} width={W} height={H} filter={`url(#r${id})`} preserveAspectRatio="none" />
        </mask>
      </defs>
      <foreignObject x={0} y={0} width={W} height={H} mask={`url(#m${id})`}>
        <div style={{position: 'relative', width: W, height: H, overflow: 'hidden'}}>{children}</div>
      </foreignObject>
      <rect x={0} y={0} width={W} height={H} fill="#0e1424" opacity={0.55} mask={`url(#k${id})`} />
    </svg>
  );
};
