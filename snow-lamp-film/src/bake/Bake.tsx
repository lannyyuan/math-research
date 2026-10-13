import React from 'react';
import {ASSETS} from './assets';

export const Bake: React.FC<{asset: string}> = ({asset}) => {
  const A = ASSETS[asset];
  if (!A) return <div>unknown asset {asset}</div>;
  return (
    <div style={{width: A.w, height: A.h, position: 'relative', background: A.format === 'jpeg' ? '#000' : 'transparent'}}>
      <A.Comp />
    </div>
  );
};
