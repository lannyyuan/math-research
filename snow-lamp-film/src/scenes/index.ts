import React from 'react';
import {S0} from './S0';
import {S1} from './S1';
import {S2} from './S2';
import {S3} from './S3';
import {S4} from './S4';
import {S5} from './S5';
import {S6} from './S6';
import {S7} from './S7';
import {S8} from './S8';
import {S9} from './S9';
import {S10} from './S10';

type SceneComp = React.FC<{len: number}>;
// 顺序必须与 src/timeline.json 里的 scenes 一一对应
export const SCENE_COMPS: Record<string, SceneComp> = {
  's0-title': S0,
  's1-lost': S1,
  's2-rabbit': S2,
  's3-turtle': S3,
  's4-river': S4,
  's5-fire': S5,
  's6-wolf': S6,
  's7-thaw': S7,
  's8-summit': S8,
  's9-farewell': S9,
  's10-window': S10,
};
