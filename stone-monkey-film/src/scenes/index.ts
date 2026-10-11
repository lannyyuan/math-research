import React from 'react';
import {S0} from './S0';
import {S1} from './S1';
import {S2} from './S2';
import {S3} from './S3';
import {S4} from './S4';
import {S5} from './S5';
import {S6} from './S6';
import {S7} from './S7';

export const SCENE_COMPS: Record<string, React.FC<{len: number}>> = {
  's0-title': S0,
  's1-dark': S1,
  's2-bridge': S2,
  's3-sea': S3,
  's4-snow': S4,
  's5-drum': S5,
  's6-lamp': S6,
  's7-epilogue': S7,
};
